// Check for saved theme in localStorage
const savedTheme = localStorage.getItem('theme');
const chkDarkMode = document.getElementById("chkDarkMode");

if (savedTheme) {
    document.body.classList.add(savedTheme);
    if (document.body.classList.contains('dark-mode')) {
        chkDarkMode.checked = true
    }
}

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
