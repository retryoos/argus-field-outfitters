// Dark mode toggle. The chosen theme is kept in local storage and applied to
// the root element so Bootstrap switches between light and dark.
(function () {
    var stored = localStorage.getItem('theme');
    if (stored) {
        document.documentElement.setAttribute('data-bs-theme', stored);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var toggle = document.querySelector('#theme-toggle');
        if (!toggle) {
            return;
        }
        toggle.addEventListener('click', function () {
            var isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
            var next = isDark ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
        });
    });
})();
