document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('menu-button');
    const navMenu = document.getElementById('nav-menu');

    if (menuButton && navMenu) {
        menuButton.addEventListener('click', function() {
            // Toggle 'hidden' and 'flex' to show/hide the menu
            navMenu.classList.toggle('hidden'); 
            navMenu.classList.toggle('flex');
            
            // Toggle a custom class for mobile-specific styling
            // This class is defined in the <style> tag in layout.html
            navMenu.classList.toggle('nav-menu-mobile-open');
        });

        // Optional: Close menu when clicking outside (more robust UX)
        document.addEventListener('click', function(event) {
            // Check if the click was outside the menu and outside the button
            if (!navMenu.contains(event.target) && !menuButton.contains(event.target) && navMenu.classList.contains('nav-menu-mobile-open')) {
                navMenu.classList.add('hidden');
                navMenu.classList.remove('flex', 'nav-menu-mobile-open');
            }
        });

        // Handle window resize: ensure menu state is correct when resizing
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768) { // Tailwind's 'md' breakpoint
                // If screen is desktop size, ensure menu is visible and styled for desktop
                navMenu.classList.remove('hidden', 'nav-menu-mobile-open');
                navMenu.classList.add('flex'); // Ensure it's flex for desktop layout
            } else {
                // If screen is mobile size, and menu is not currently open, ensure it's hidden
                // If it IS open, ensure mobile styles are applied.
                if (!navMenu.classList.contains('nav-menu-mobile-open')) {
                    navMenu.classList.add('hidden');
                    navMenu.classList.remove('flex');
                } else {
                    // If menu is open on mobile, make sure mobile styles are active
                    navMenu.classList.add('flex', 'nav-menu-mobile-open');
                    navMenu.classList.remove('hidden');
                }
            }
        });

        // Initialize state on load based on screen width
        // If loaded on desktop, ensure menu is visible
        if (window.innerWidth >= 768) {
            navMenu.classList.remove('hidden', 'nav-menu-mobile-open');
            navMenu.classList.add('flex');
        } else {
            navMenu.classList.add('hidden');
            navMenu.classList.remove('flex', 'nav-menu-mobile-open');
        }
    }
});