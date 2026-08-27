document.addEventListener('DOMContentLoaded', function () {
    const logoElements = document.querySelectorAll('.logo-reload');
    logoElements.forEach(logo => {
        logo.addEventListener('click', function (e) {
            e.preventDefault();
            window.location.reload();
        });
    });

    const gearBtn = document.getElementById('gearBtn');
    const userDropdown = document.getElementById('userDropdown');

    if (gearBtn && userDropdown) {
        gearBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });

        document.addEventListener('click', function (e) {
            if (!userDropdown.contains(e.target) && e.target !== gearBtn) {
                userDropdown.classList.remove('active');
            }
        });
    }
});

