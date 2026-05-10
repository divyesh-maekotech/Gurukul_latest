// Header and Footer Include System
console.log('includes.js loaded successfully');

class ComponentLoader {
    constructor() {
        this.loadComponents();
    }

    async loadComponents() {
        console.log('Starting to load components...');
        try {
            // Load header and footer simultaneously
            await Promise.all([
                this.loadComponent('header-placeholder', 'components/header.html'),
                this.loadComponent('footer-placeholder', 'components/footer.html')
            ]);
            
            console.log('All components loaded successfully');
            // Initialize navigation after components load
            this.initializeNavigation();
        } catch (error) {
            console.error('Error loading components:', error);
            this.showError();
        }
    }

    async loadComponent(elementId, filePath) {
        console.log(`Loading ${filePath} into ${elementId}`);
        try {
            const response = await fetch(filePath);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} for ${filePath}`);
            }
            const html = await response.text();
            const element = document.getElementById(elementId);
            if (element) {
                element.innerHTML = html;
                console.log(`Successfully loaded ${filePath}`);
            } else {
                console.error(`Element with ID ${elementId} not found`);
            }
        } catch (error) {
            console.error(`Error loading ${filePath}:`, error);
            throw error;
        }
    }

    initializeNavigation() {
        console.log('Initializing navigation...');
        // Highlight current page in navigation
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';
        const navLinks = document.querySelectorAll('.nav-links a');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPage) {
                link.classList.add('active');
                console.log(`Added active class to ${currentPage}`);
            }
        });

        // Mobile menu toggle (if you add mobile navigation later)
        const mobileToggle = document.querySelector('.mobile-toggle');
        const navLinksContainer = document.querySelector('.nav-links');
        
        if (mobileToggle && navLinksContainer) {
            mobileToggle.addEventListener('click', () => {
                navLinksContainer.classList.toggle('active');
            });
        }
    }

    showError() {
        // Fallback content if loading fails
        console.log('Showing fallback content due to loading error');
        
        const headerFallback = `
            <header style="background-color: #2c3e50; color: white; padding: 1rem;">
                <nav style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
                    <div class="logo">
                        <h1>Your Logo</h1>
                    </div>
                    <ul style="display: flex; list-style: none; gap: 2rem; margin: 0; padding: 0;">
                        <li><a href="index.html" style="color: white; text-decoration: none; padding: 0.5rem 1rem;">Home</a></li>
                        <li><a href="about.html" style="color: white; text-decoration: none; padding: 0.5rem 1rem;">About</a></li>
                        <li><a href="blog.html" style="color: white; text-decoration: none; padding: 0.5rem 1rem;">Blog</a></li>
                        <li><a href="contact.html" style="color: white; text-decoration: none; padding: 0.5rem 1rem;">Contact</a></li>
                    </ul>
                </nav>
            </header>
        `;
        
        const footerFallback = `
            <footer style="background-color: #34495e; color: white; padding: 2rem 0; margin-top: auto;">
                <div style="text-align: center;">
                    <p>&copy; 2025 Your Website. All rights reserved.</p>
                    <p style="margin-top: 1rem;">
                        <a href="index.html" style="color: #bdc3c7; margin: 0 1rem;">Home</a>
                        <a href="about.html" style="color: #bdc3c7; margin: 0 1rem;">About</a>
                        <a href="blog.html" style="color: #bdc3c7; margin: 0 1rem;">Blog</a>
                        <a href="contact.html" style="color: #bdc3c7; margin: 0 1rem;">Contact</a>
                    </p>
                </div>
            </footer>
        `;
        
        const headerElement = document.getElementById('header-placeholder');
        const footerElement = document.getElementById('footer-placeholder');
        
        if (headerElement) headerElement.innerHTML = headerFallback;
        if (footerElement) footerElement.innerHTML = footerFallback;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ComponentLoader');
    new ComponentLoader();
});