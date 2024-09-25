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
