from django.contrib import admin
from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Exercise, Comment, ContactMessage, CommentReport
from cloudinary import CloudinaryImage
from django.utils.html import format_html


class ExerciseAdminForm(forms.ModelForm):
    """
    A form for managing Exercise instances in the admin interface.

    This form uses Summernote for rich text editing of the description fields.

    Meta:
        model: The Exercise model.
        fields: All fields in the Exercise model.
        widgets: Custom widgets for specific fields
        to enhance editing experience.
    """

    class Meta:
        model = Exercise
        fields = "__all__"
        widgets = {
            "description1": SummernoteWidget(),
            "detailed_description1": SummernoteWidget(),
            "detailed_description2": SummernoteWidget(),
        }


class CommentAdminForm(forms.ModelForm):
    """
    A form for managing Comment instances in the admin interface.

    This form uses Summernote for rich text editing of the body field.

    Meta:
        model: The Comment model.
        fields: All fields in the Comment model.
        widgets: Custom widgets for specific fields
        to enhance editing experience.
    """

    class Meta:
        model = Comment
        fields = "__all__"
        widgets = {
            "body": SummernoteWidget(),  # Use Summernote for the body field
        }


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Exercise instances.

    This customization allows for enhanced editing of Exercise fields
    and includes features like image preview.

    Attributes:
        form: The custom form used for editing Exercise instances.
        list_display: Fields to display in the list view.
        search_fields: Fields to include in the search functionality.
        list_filter: Fields to filter by in the list view.
    """

    form = ExerciseAdminForm  # Use the custom form with Summernote
    list_display = (
        "title",
        "description",
        "detailed_description1",
        "detailed_description2",
        "created_at",
        "image_tag",
    )
    search_fields = (
        "title",
        "description",
        "detailed_description1",
        "detailed_description2",
    )
    list_filter = ("created_at",)

    def image_tag(self, obj):
        """
        Returns an HTML image tag for displaying the Exercise's image.

        Args:
            obj: The Exercise instance.

        Returns:
            str: An HTML string containing the image
            tag or a message if no image is present.
        """
        if obj.image:
            webp_url = CloudinaryImage(obj.image.public_id).build_url(
                format="webp"
            )
            return format_html(
                '<img src="{}" width="100" height="100" />', webp_url
            )
        return "No image"

    image_tag.short_description = "Image"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Comment instances.

    This customization provides a user-friendly interface for reviewing
    and editing comments on exercises.

    Attributes:
        form: The custom form used for editing Comment instances.
        list_display: Fields to display in the list view.
        search_fields: Fields to include in the search functionality.
        list_filter: Fields to filter by in the list view.
    """

    form = CommentAdminForm  # Use the custom form with Summernote
    list_display = ("exercise", "user", "created_on", "approved")
    search_fields = ("exercise__title", "user__username", "body")
    list_filter = (
        "approved",
        "created_on",
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing ContactMessage instances.

    This customization allows for viewing contact messages submitted by users.

    Attributes:
        readonly_fields: Fields that cannot be edited in the admin interface.
        list_display: Fields to display in the list view.
        search_fields: Fields to include in the search functionality.
        list_filter: Fields to filter by in the list view.
    """

    readonly_fields = ("name", "email", "message", "created_at")
    list_display = ("name", "email", "message", "created_at")
    search_fields = ("name", "email", "message")
    list_filter = ("name", "created_at")


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    """
    Admin interface for managing CommentReport instances.

    This customization allows for reviewing reports submitted by users
    regarding specific comments.

    Attributes:
        readonly_fields: Fields that cannot be edited in the admin interface.
        list_display: Fields to display in the list view.
        list_filter: Fields to filter by in the list view.
        search_fields: Fields to include in the search functionality.
    """

    readonly_fields = ("user", "comment", "reason", "created_at")
    list_display = ("user", "comment", "reason", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "comment__body", "reason")
