/* jshint esversion: 6 */
/* global bootstrap */

(function() {
    // First, check if the script has already run. If it has, skip everything to avoid running the same logic twice.
    if (window.contactScriptInitialized) {
        console.log('Contact script already initialized. Skipping.');
        return; // Exit if already initialized
    }
    window.contactScriptInitialized = true; // Mark the script as initialized

    console.log('Initializing contact script at', new Date().toISOString());

    // The URL for the contact form, this will be used to load the form via AJAX
    const contactFormUrl = "{% url 'contact_form' %}";

    // When the user clicks the contact button, display the contact form modal
    $('#contactButton').off('click').on('click', function () {
        console.log('Contact button clicked at', new Date().toISOString());
        $('#contactModal').modal('show'); // Show the contact modal

        // Load the contact form content via AJAX
        $.ajax({
            url: contactFormUrl, // Load the form from this URL
            type: 'GET', // Make a GET request to fetch the form
            success: function (data) {
                console.log('Contact form loaded successfully at', new Date().toISOString());
                $('#contactModal .modal-body').html(data); // Insert the loaded form into the modal body
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed:", status, error);
                // If there's an error, display a message in the modal body
                $('#contactModal .modal-body').html('<p>There was an error loading the form.</p>');
            }
        });
    });

    // Handles form submission when the user submits the contact form inside the modal
    $(document).off('submit', '#contactForm').on('submit', '#contactForm', function (event) {
        event.preventDefault(); // Prevent the form from submitting the usual way (i.e., page refresh)
        console.log('Contact form submitted at', new Date().toISOString());

        var $form = $(this); // The form element
        var $submitButton = $form.find('button[type="submit"]'); // The submit button in the form

        // Check if the form is already in the process of being submitted
        if ($submitButton.data('submitting')) {
            console.log('Form already submitting, ignoring request');
            return; // If it's already submitting, stop further submissions
        }

        $submitButton.data('submitting', true); // Set the submitting flag to avoid double submissions

        // Send the form data via AJAX
        $.ajax({
            url: $form.attr('action'), // The form's action URL
            type: 'POST', // Send the data via POST
            data: $form.serialize(), // Convert the form data to a URL-encoded string
            success: function (response) {
                console.log('Contact form submission successful at', new Date().toISOString(), response);
                // On success, show a thank you message in the modal
                $('#contactModal .modal-body').html('<h5>Thank You!</h5><p>Thank you for contacting us!</p>');
                
                // Hide the modal after a 2-second delay to allow the user to see the thank-you message
                setTimeout(function () {
                    $('#contactModal').modal('hide');
                    console.log('Contact modal hidden at', new Date().toISOString());
                }, 2000); // 2-second delay
            },
            error: function (xhr, status, error) {
                console.error("Contact form submission failed:", status, error);
                // If the submission fails, show an error message
                $('#contactModal .modal-body').html('<p>There was an error with your submission.</p>');
            },
            complete: function () {
                $submitButton.data('submitting', false); // Reset the submitting flag after the request is complete
            }
        });
    });

    // Finally, when the modal is closed, clear its contents to make sure the form is always fresh next time it's opened
    $('#contactModal').on('hidden.bs.modal', function () {
        console.log('Contact modal hidden at', new Date().toISOString());
        var modalBody = $(this).find('.modal-body');
        modalBody.html(''); // Clear the modal body content
    });
})();
