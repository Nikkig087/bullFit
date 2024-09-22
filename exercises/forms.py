from django import forms
from .models import Comment, ContactMessage
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm


class CommentForm(forms.ModelForm):
    """
    A form for creating and editing comments.

    This form is based on the Comment model and allows users
    to submit their comments.

    Meta:
        model: The Comment model.
        fields: List of fields to include in the form, excluding 'author'.
    """
    
    class Meta:
        model = Comment
        fields = ["body"]  # Ensure 'author' is not included here


class CustomSignupForm(SignupForm):
    """
    Custom signup form for user registration.

    Extends the default SignupForm from allauth to include additional
    fields for user creation.

    Meta:
        model: The User model.
        fields: List of fields to include in the signup form.
    """
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("This field is required.")
        return email


class ReportCommentForm(forms.Form):
    """
    A form for reporting comments.

    This form allows users to specify a reason for reporting a comment.

    Fields:
        comment_text: The text of the comment being reported (read-only).
        reason: The reason for reporting the comment.
    """
    
    comment_text = forms.CharField(
        widget=forms.Textarea(attrs={"readonly": "readonly"})
    )
    reason = forms.CharField(
        widget=forms.Textarea, label="Reason for Reporting"
    )
