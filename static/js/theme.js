// Dark mode toggle. The chosen theme is kept in local storage and applied to
// the root element so Bootstrap switches between light and dark. This file
// loads in the head so the saved theme applies before the page paints.
(function () {
    // Reapply the choice saved on an earlier visit if there is one.
    var stored = localStorage.getItem('theme');
    if (stored) {
        document.documentElement.setAttribute('data-bs-theme', stored);
    }

    // The toggle button only exists once the body is parsed, so the click
    // listener is attached after the page is ready.
    document.addEventListener('DOMContentLoaded', function () {
        var toggle = document.querySelector('#theme-toggle');
        if (!toggle) {
            return;
        }
        toggle.addEventListener('click', function () {
            // Bootstrap reads the data-bs-theme attribute on the html tag.
            var isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
            var next = isDark ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
        });
    });
})();
