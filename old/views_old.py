from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Exercise, Comment, CommentReport
from .forms import CommentForm, ContactMessageForm, ReportCommentForm
from django.views import generic
from django.http import JsonResponse


class ExerciseListView(generic.ListView):
    """
    Displays a list of exercises with pagination.

    Attributes:
        model: The Exercise model.
        template_name: The template to render.
        context_object_name: The context variable name for the exercises.
        paginate_by: Number of exercises to display per page.

    Methods:
        get_context_data: Adds a contact form to the context.
        get_queryset: Orders exercises by title for display.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contact_form"] = ContactMessageForm()
        return context

    def get_queryset(self):
        return Exercise.objects.order_by("title")


def exercise_detail(request, pk):
    """
    Displays the details of a specific exercise along with its comments.

    Args:
        request: The HTTP request object.
        pk: The primary key of the exercise to display.

    Returns:
        Rendered exercise detail page with comments.
    """
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
    """
    Edits an existing comment for a specific exercise.

    Args:
        request: The HTTP request object.
        pk: The primary key of the exercise.
        comment_id: The ID of the comment to edit.

    Returns:
        Rendered edit comment page or redirects to exercise detail after saving.
    """
    exercise = get_object_or_404(Exercise, pk=pk)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("exercise_detail", pk=exercise.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, "exercises/edit_comment.html", {
        "exercise": exercise,
        "comment": comment,
        "form": form,
    })


@login_required
def add_comment(request, pk):
    """
    Adds a new comment to a specific exercise.

    Args:
        request: The HTTP request object.
        pk: The primary key of the exercise to which the comment is added.

    Returns:
        Rendered add comment page or redirects to exercise detail after saving.
    """
    exercise = get_object_or_404(Exercise, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.exercise = exercise
            comment.user = request.user
            comment.save()
            messages.success(request, "Your comment has been added and is awaiting approval.")
            return redirect("exercise_detail", pk=exercise.pk)
    else:
        form = CommentForm()

    return render(request, "exercises/add_comment.html", {
        "form": form,
        "exercise": exercise,
    })


@login_required
def delete_comment(request, pk, comment_id):
    """
    Deletes a comment from a specific exercise.

    Args:
        request: The HTTP request object.
        pk: The primary key of the exercise.
        comment_id: The ID of the comment to delete.

    Returns:
        Redirects to the exercise detail page after deletion.
    """
    exercise = get_object_or_404(Exercise, pk=pk)
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user:
        comment.delete()
        messages.success(request, "Comment deleted!")
    else:
        messages.error(request, "You can only delete your own comments!")

    return redirect("exercise_detail", pk=pk)


def contact_form(request):
    """
    Displays and processes the contact form.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered contact form page or redirects after successful submission.
    """
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your message. We will get back to you soon!")
            return redirect("home")
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = ContactMessageForm()

    return render(request, "exercises/contact_form.html", {"form": form})


def report_comment(request, comment_id):
    """
    Handles reporting a comment.

    Args:
        request: The HTTP request object.
        comment_id: The ID of the comment to report.

    Returns:
        JSON response for AJAX submissions or renders the report comment form.
    """
    if not request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"redirect_url": "/accounts/login/"}, status=403)
        return redirect("login")

    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        form = ReportCommentForm(request.POST)
        if form.is_valid():
            CommentReport.objects.create(
                user=request.user,
                comment=comment,
                reason=form.cleaned_data["reason"],
            )
            return JsonResponse({"message": "Comment reported successfully!"})
        else:
            return JsonResponse({"message": "Error reporting comment"}, status=400)

    else:
        form = ReportCommentForm(
            initial={
                "comment_id": comment.id,
                "comment_text": comment.body,
            }
        )

    return render(request, "exercises/report_comment_form.html", {"form": form, "comment": comment})


def custom_404_view(request, exception):
    """
    Renders a custom 404 error page.

    Args:
        request: The HTTP request object.
        exception: The exception raised for the 404 error.

    Returns:
        Rendered custom 404 error page.
    """
    return render(request, "exercises/404.html", status=404)
