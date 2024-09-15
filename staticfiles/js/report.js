(function() {
    if (window.reportCommentScriptInitialized) {
        console.log('Report comment script already initialized. Skipping.');
        return;
    }
    window.reportCommentScriptInitialized = true;

    console.log('Initializing report comment script at', new Date().toISOString());

    // Report Comment Modal Logic
    $(document).on('click', '.report-comment-button', function () {
        console.log('Report comment button clicked at', new Date().toISOString());
        const commentId = $(this).data('comment-id');
        const url = `/report_comment_form/${commentId}/`;

        // Load the report comment form via AJAX
        $.ajax({
            url: url,
            type: 'GET',
            success: function (data) {
                console.log('Report comment form loaded successfully at', new Date().toISOString());
                $('#reportModal .modal-body').html(data); // Inject the form HTML into the modal
                $('#reportModal').modal('show'); // Show the modal
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed:", status, error);
                $('#reportModal .modal-body').html('<p>There was an error loading the form.</p>');
                if (xhr.status === 403) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url; // Redirect to login page
                        }
                    } catch (e) {
                        console.error('Failed to parse JSON from response:', e);
                        $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>');
                    }
                }
            }
        });
    });

    // Report Comment Form Submission Logic
    $(document).on('submit', '#reportCommentForm', function (event) {
        event.preventDefault();
        console.log('Report comment form submitted at', new Date().toISOString());

        const $form = $(this);
        const $submitButton = $form.find('button[type="submit"]');

        if ($submitButton.data('submitting')) {
            console.log('Form already submitting, ignoring request');
            return; // Prevent multiple submissions
        }

        $submitButton.data('submitting', true); // Set submitting flag

        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                console.log('Report comment form submission successful at', new Date().toISOString(), response);
                $('#reportModal .modal-body').html('<h5>Thank You!</h5><p>Your report has been submitted.</p>');
                setTimeout(function () {
                    $('#reportModal').modal('hide'); // Hide the modal
                    console.log('Report modal hidden at', new Date().toISOString());
                }, 2000); // Delay to show the thank-you message
            },
            error: function (xhr, status, error) {
                console.error("Report comment form submission failed:", status, error);
                $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>');
                if (xhr.status === 403) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url; // Redirect to login page
                        }
                    } catch (e) {
                        console.error('Failed to parse JSON from response:', e);
                        $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>');
                    }
                }
            },
            complete: function () {
                $submitButton.data('submitting', false); // Reset flag
            }
        });
    });

    // Reset report modal content when hidden
    $('#reportModal').on('hidden.bs.modal', function () {
        console.log('Report modal hidden at', new Date().toISOString());
        const modalBody = $(this).find('.modal-body');
        modalBody.html(''); // Clear the content to ensure it loads fresh next time
    });

    // Utility function to get the CSRF token from cookies
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
        return cookieValue;
    }
})();
