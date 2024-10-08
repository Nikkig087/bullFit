from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Exercise, Comment, CommentReport
from .forms import CommentForm
from django.views import generic
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import ContactMessageForm, ReportCommentForm
from django.db import models
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class ExerciseListView(generic.ListView):
    model = Exercise
    template_name = "exercises/exercise_list.html"
    context_object_name = "exercises"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_form"] = (
            ContactMessageForm()
        )  # Use 'contact_form' to avoid confusion
        return context

    def get_queryset(self):
        return Exercise.objects.order_by("title")  # Ordered by title


def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    comments = exercise.comments.all()
    comment_form = CommentForm()
    comment_count = comments.count()

    context = {
        "exercise": exercise,
        "comments": comments,
        "comment_count": comment_count,
        "comment_form": comment_form,
    }

    return render(request, "exercises/exercise_detail.html", context)


@login_required
def edit_comment(request, pk, comment_id):
    exercise = get_object_or_404(Exercise, pk=pk)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("exercise_detail", pk=exercise.pk)
    else:
        form = CommentForm(instance=comment)
    return render(
        request,
        "exercises/edit_comment.html",
        {
            "exercise": exercise,
            "comment": comment,
            "form": form,
        },
    )


@login_required
def add_comment(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.exercise = exercise
            comment.user = request.user
            comment.save()
            messages.success(
                request,
                "Your comment has been added and is awaiting approval.",
            )
            return redirect("exercise_detail", pk=exercise.pk)
    else:
        form = CommentForm()
    return render(
        request,
        "exercises/add_comment.html",
        {"form": form, "exercise": exercise},
    )


@login_required
def delete_comment(request, pk, comment_id):
    exercise = get_object_or_404(Exercise, pk=pk)
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user:
        comment.delete()
        messages.add_message(request, messages.SUCCESS, "Comment deleted!")
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "You can only delete your own comments!",
        )
    return redirect("exercise_detail", pk=pk)


def contact_form(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you for your message. We will get back to you soon!",
            )
            return redirect(
                "home"
            )
        else:
            messages.error(
                request, "There was an error with your submission."
            )
    else:
        form = ContactMessageForm()
    return render(request, "exercises/contact_form.html", {"form": form})


def report_comment(request, comment_id):

    if not request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"redirect_url": "/accounts/login/"}, status=403
            )

        return redirect("login")

    comment = get_object_or_404(Comment, id=comment_id)

    # Handle POST request for submitting the report

    if request.method == "POST":
        form = ReportCommentForm(request.POST)
        if form.is_valid():
            # Create the comment report

            CommentReport.objects.create(
                user=request.user,
                comment=comment,
                reason=form.cleaned_data["reason"],
            )
            return JsonResponse(
                {"message": "Comment reported successfully!"}
            )
        else:
            return JsonResponse(
                {"message": "Error reporting comment"}, status=400
            )
    # For GET requests, render the form (if needed for the modal)

    else:
        form = ReportCommentForm(
            initial={
                "comment_id": comment.id,
                "comment_text": comment.body,
            }
        )
    # Render the form for the report modal (if not using AJAX to submit)

    return render(
        request,
        "exercises/report_comment_form.html",
        {"form": form, "comment": comment},
    )


def custom_404_view(request, exception):
    return render(request, "exercises/404.html", status=404)
