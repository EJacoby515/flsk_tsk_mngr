$(document).ready(function() {
    // Open modal and populate form fields
    $('#editTaskModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var taskId = button.data('task-id');
        var taskTitle = button.data('task-title');
        var taskDescription = button.data('task-description');
        var taskPriority = button.data('task-priority');
        var taskStatus = button.data('task-status');

        var modal = $(this);
        modal.find('#edit-task-id').val(taskId);
        modal.find('#edit-title').val(taskTitle);
        modal.find('#edit-description').text(taskDescription);
        modal.find('#edit-priority').val(taskPriority);
        modal.find('#edit-status').val(taskStatus);

        // Set the task_id in the form's action URL
        var formAction = $('#edit-task-form').attr('action');
        formAction = formAction.slice(0, -1) + taskId;
        $('#edit-task-form').attr('action', formAction);
    });

    // Prevent modal from blocking the entire page
    $('body').on('shown.bs.modal', '.modal', function() {
        $('body').addClass('modal-open');
    }).on('hidden.bs.modal', '.modal', function() {
        $('body').removeClass('modal-open');
    });

    // Close modal when clicking outside
    $(document).on('click', '.modal-backdrop', function(event) {
        $('.modal').modal('hide');
    });

    // Handle form submission
    $('#edit-task-form').on('submit', function(event) {
        event.preventDefault();

        var form = $(this);
        var url = form.attr('action');
        var formData = form.serialize();

        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            success: function(response) {
                // Handle successful response
                console.log(response);
                // Reload the page or update the task list
                location.reload();
            },
            error: function(xhr, status, error) {
                // Handle error
                console.error(error);
            }
        });
    });

    // Toggle navigation menu on smaller screens
    const navToggle = $('.nav-toggle');
    const navMenu = $('.nav-menu');

    navToggle.on('click', function() {
        navMenu.toggleClass('active');
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const passwordToggles = document.querySelectorAll('.password-toggle');

    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const passwordField = this.parentElement.previousElementSibling;

            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                this.querySelector('i').classList.remove('fa-eye-slash');
                this.querySelector('i').classList.add('fa-eye');
            } else {
                passwordField.type = 'password';
                this.querySelector('i').classList.remove('fa-eye');
                this.querySelector('i').classList.add('fa-eye-slash');
            }
        });
    });
});