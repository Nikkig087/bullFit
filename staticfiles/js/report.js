/* jshint esversion: 6 */
/* global $ */
(function() {
    // Check if the script for reporting comments has already been initialized. If so, log it and skip running the script again.
    if (window.reportCommentScriptInitialized) {
        console.log('Report comment script already initialized. Skipping.');
        return;
    }
    window.reportCommentScriptInitialized = true; // Mark the script as initialized so it won't run again.

    console.log('Initializing report comment script at', new Date().toISOString());

    // When any "Report Comment" button is clicked, load the report form in a modal.
    $(document).on('click', '.report-comment-button', function () {
        console.log('Report comment button clicked at', new Date().toISOString());

        const commentId = $(this).data('comment-id'); // Get the comment ID from the button's data attribute
        const url = `/report_comment_form/${commentId}/`; // Construct the URL to fetch the report form

        // Use AJAX to load the report comment form
        $.ajax({
            url: url,
            type: 'GET',
            success: function (data) {
                console.log('Report comment form loaded successfully at', new Date().toISOString());
                $('#reportModal .modal-body').html(data); // Insert the form into the modal
                $('#reportModal').modal('show'); // Show the modal to the user
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed:", status, error);
                $('#reportModal .modal-body').html('<p>There was an error loading the form.</p>'); // Show error in modal

                // If the error status is 403, it might be a permission issue, such as the user needing to log in
                if (xhr.status === 403) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url; // Redirect to the login page if necessary
                        }
                    } catch (e) {
                        console.error('Failed to parse JSON from response:', e);
                        $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>');
                    }
                }
            }
        });
    });

    // When the report comment form is submitted, handle the form submission via AJAX
    $(document).on('submit', '#reportCommentForm', function (event) {
        event.preventDefault(); // Stop the form from submitting the traditional way
        console.log('Report comment form submitted at', new Date().toISOString());

        const $form = $(this); // Reference to the form being submitted
        const $submitButton = $form.find('button[type="submit"]'); // Find the submit button in the form

        // Check if the form is already in the process of being submitted to prevent duplicate submissions
        if ($submitButton.data('submitting')) {
            console.log('Form already submitting, ignoring request');
            return;
        }

        $submitButton.data('submitting', true); // Set a flag to indicate that the form is currently submitting

        // Send the form data via AJAX
        $.ajax({
            url: $form.attr('action'), // Use the form's action URL
            type: 'POST',
            data: $form.serialize(), // Serialize the form data to be sent
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Add the CSRF token from cookies for security
            },
            success: function (response) {
                console.log('Report comment form submission successful at', new Date().toISOString(), response);
                $('#reportModal .modal-body').html('<h5>Thank You!</h5><p>Your report has been submitted.</p>'); // Show a thank you message
                setTimeout(function () {
                    $('#reportModal').modal('hide'); // Close the modal after 2 seconds
                    console.log('Report modal hidden at', new Date().toISOString());
                }, 2000); // 2-second delay
            },
            error: function (xhr, status, error) {
                console.error("Report comment form submission failed:", status, error);
                $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>'); // Show an error message

                // Handle permission errors similarly to the form loading logic
                if (xhr.status === 403) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url; // Redirect to login page if needed
                        }
                    } catch (e) {
                        console.error('Failed to parse JSON from response:', e);
                        $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>');
                    }
                }
            },
            complete: function () {
                $submitButton.data('submitting', false); // Reset the flag so the form can be submitted again
            }
        });
    });

    // Clear the modal content when it's closed, so the form is reloaded fresh next time
    $('#reportModal').on('hidden.bs.modal', function () {
        console.log('Report modal hidden at', new Date().toISOString());
        const modalBody = $(this).find('.modal-body');
        modalBody.html(''); // Clear the modal body content
    });

    // Utility function to get the CSRF token from the cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue; // Return the CSRF token value
    }
})();
