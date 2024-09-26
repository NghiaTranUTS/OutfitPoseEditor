// Check for saved theme in localStorage
const savedTheme = localStorage.getItem('theme');
const chkDarkMode = document.getElementById("chkDarkMode");
const ball = document.querySelector('.checkbox-label .ball');

if (savedTheme) {
  document.body.classList.add(savedTheme);
  if (document.body.classList.contains('dark-mode')) {
    chkDarkMode.checked = true
  }
}
// Now that the page has loaded and the theme is set, enable the transition
setTimeout(() => {
  ball.style.transition = 'transform 0.2s linear';  // Enable the transition after initial load
}, 100);

chkDarkMode.addEventListener("change", () => {
  if (chkDarkMode.checked === true) {
    document.body.classList.add('dark-mode');
  } else {
    document.body.classList.remove('dark-mode');
  }
  const theme = document.body.classList.contains('dark-mode') ? 'dark-mode' : '';
  // Save theme preference in localStorage
  localStorage.setItem('theme', theme);
});


$(document).ready(function () {
  // Handle contact form submission via AJAX
  $('#contact-form').on('submit', function (e) {
    e.preventDefault(); // Prevent the default form submission

    // Gather form data
    const formData = {
      name: $('#name').val(),
      email: $('#email').val(),
      message: $('#message').val()
    };

    // Send form data via AJAX
    $.ajax({
      url: $(this).attr('action'),
      type: 'POST',
      data: formData,
      success: function (response) {
        // Clear form fields
        $('#name').val('');
        $('#email').val('');
        $('#message').val('');

        // Show success message
        showAlert(response.message, 'success');
      },
      error: function () {
        // Show error message
        showAlert('There was an error sending your message. Please try again later.', 'danger');
      }
    });
  });

  // Function to show flash messages dynamically
  function showAlert(message, category) {
    const alertHTML = `
      <div class="alert alert-${category} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
    `;

    $('#alert-container').html(alertHTML); // Insert the alert into the container

    // Automatically hide the alert after 5 seconds
    setTimeout(function () {
      $('.alert').alert('close');
    }, 5000);
  }
});