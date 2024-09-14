(function() {
    if (window.reportCommentScriptInitialized) {
        console.log('Report comment script already initialized. Skipping.');
        return;
    }
    window.reportCommentScriptInitialized = true;

    console.log('Initializing report comment script at', new Date().toISOString());

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

    // Ensure csrftoken is declared only once
    const csrftoken = getCookie('csrftoken');

    $(document).on('click', '.report-comment-button', function () {
        console.log('Report comment button clicked at', new Date().toISOString());
        const commentId = $(this).data('comment-id');
        const url = `/report_comment_form/${commentId}/`;

        $.ajax({
            url: url,
            type: 'GET',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (data) {
                console.log('Report comment form loaded successfully at', new Date().toISOString(), data);
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
                } else {
                    $('#reportModal .modal-body').html('<p>There was an error with your submission.</p>');
                }
            }
        });
    });

    $('#reportModal').on('show.bs.modal', function () {
        console.log('Report modal shown at', new Date().toISOString());
        $(this).find('.dropdown-menu.show').removeClass('show');
    });

    $('#reportModal').on('hidden.bs.modal', function () {
        console.log('Report modal hidden at', new Date().toISOString());
        const modalBody = $(this).find('.modal-body');
        modalBody.html('');
    });

})();
