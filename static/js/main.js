
        // Loading Screen
        window.addEventListener('load', function() {
            setTimeout(() => {
                document.getElementById('loadingOverlay').classList.add('hidden');
            }, 1000);
        });

        // Navigation scroll effect
        window.addEventListener('scroll', function() {
            const nav = document.getElementById('mainNav');
            if (window.scrollY > 100) {
                // nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }

            // Back to top button visibility
            const backToTop = document.getElementById('backToTop');
            if (window.scrollY > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        });

        // Scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.fade-in').forEach(el => {
            observer.observe(el);
        });

        // Show Section Function
  function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
       section.classList.remove('visible');
        observer.observe(targetSection);
    });

    // Remove active class from all nav links
    // const navLinks = document.querySelectorAll('.nav-link');
    // navLinks.forEach(link => {
    //     link.classList.remove('active');
    // });
const targetSection = document.getElementById(sectionId);
if (targetSection) {
    targetSection.style.display = 'block';
    targetSection.classList.add('fade-in');

    // Re-observe all fade-in elements inside the target section
    targetSection.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

    setTimeout(() => {
        targetSection.classList.add('visible');
    }, 50);

    // targetSection.scrollIntoView({
    //     behavior: 'smooth',
    //     block: 'start',
    //     inline: 'nearest'
    // });
}
    // Show target section with animation
  
    // Add active class to clicked link
    const activeLink = document.querySelector(`a[onclick="showSection('${sectionId}')"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

        // Contact Form Functions
        function getFormData() {
            return {
                name: document.getElementById('contactName').value,
                email: document.getElementById('contactEmail').value,
                phone: document.getElementById('contactPhone')?.value || '',
                subject: document.getElementById('contactSubject').value,
                message: document.getElementById('contactMessage').value
            };
        }

        function sendViaEmail() {
            const { name, email, phone, subject, message } = getFormData();
            
            if (!name || !email || !subject || !message) {
                showAlert('Please fill in all required fields', 'warning');
                return;
            }
            
            const emailAddress = 'gurukultrustrsbd@gmail.com';
            const mailSubject = encodeURIComponent(`Temple Inquiry: ${subject}`);
            const mailBody = encodeURIComponent(
                `नमस्ते!\n\nName: ${name}\nEmail: ${email}\nPhone: ${phone}\n\nSubject: ${subject}\n\nMessage:\n${message}\n\nBest regards,\n${name}`
            );
            
            const mailtoLink = `mailto:${emailAddress}?subject=${mailSubject}&body=${mailBody}`;
            window.location.href = mailtoLink;
            
            showAlert('Email client opened successfully!', 'success');
        }

        function sendViaWhatsApp() {
            const { name, email, phone, subject, message } = getFormData();
            
            if (!name || !subject || !message) {
                showAlert('Please fill in required fields', 'warning');
                return;
            }
            
            const whatsappNumber = '918233199334';
            const whatsappMessage = encodeURIComponent(
                `🙏 नमस्ते!\n\n📩 Temple Inquiry:\n\n👤 Name: ${name}\n📧 Email: ${email}\n📱 Phone: ${phone}\n📝 Subject: ${subject}\n\n💬 Message:\n${message}\n\nThank you!`
            );
            
            const whatsappLink = `https://wa.me/${whatsappNumber}?text=${whatsappMessage}`;
            window.open(whatsappLink, '_blank');
            
            showAlert('WhatsApp opened successfully!', 'success');
        }

        // Booking Functions
        function searchRooms() {
            const checkIn = document.getElementById('checkInDate').value;
            const checkOut = document.getElementById('checkOutDate').value;
            const guests = document.getElementById('guestCount').value;
            const roomType = document.getElementById('roomType').value;
            
            if (!checkIn || !checkOut) {
                showAlert('Please select check-in and check-out dates', 'warning');
                return;
            }
            
            if (new Date(checkIn) >= new Date(checkOut)) {
                showAlert('Check-out date must be after check-in date', 'danger');
                return;
            }
            
            if (new Date(checkIn) < new Date()) {
                showAlert('Check-in date cannot be in the past', 'warning');
                return;
            }
            
            // Show loading and simulate API call
            showAlert('Searching for available rooms...', 'info');
            
            setTimeout(() => {
                showAlert('Search completed! Please call +91-82 3319 9334 for availability and booking.', 'success');
            }, 2000);
        }

        function submitBooking() {
            const customerName = document.getElementById('customerName').value;
            const customerEmail = document.getElementById('customerEmail').value;
            const customerPhone = document.getElementById('customerPhone').value;
            
            if (!customerName || !customerEmail || !customerPhone) {
                showAlert('Please fill in all required fields', 'warning');
                return;
            }
            
            // Show loading
            showAlert('Processing your booking...', 'info');
            
            // Simulate booking submission
            setTimeout(() => {
                showAlert('Booking request submitted! We will contact you shortly for confirmation.', 'success');
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
                modal.hide();
                document.getElementById('completeBookingForm').reset();
            }, 2000);
        }

        // Utility Functions
        function showAlert(message, type = 'info') {
            // Remove existing alerts
            const existingAlerts = document.querySelectorAll('.floating-alert');
            existingAlerts.forEach(alert => alert.remove());
            
            // Create new alert
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} floating-alert position-fixed shadow-lg`;
            alertDiv.style.cssText = `
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                animation: slideInRight 0.3s ease-out;
            `;
            
            const iconMap = {
                'success': 'fas fa-check-circle',
                'warning': 'fas fa-exclamation-triangle',
                'danger': 'fas fa-times-circle',
                'info': 'fas fa-info-circle'
            };
            
            alertDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="${iconMap[type]} me-2"></i>
                    <span>${message}</span>
                    <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
                </div>
            `;
            
            document.body.appendChild(alertDiv);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.style.animation = 'slideOutRight 0.3s ease-out';
                    setTimeout(() => alertDiv.remove(), 300);
                }
            }, 5000);
        }

        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        function openGoogleMaps() {
            const address = "Shri Bhattarak Yashkirti Digamber Jain Mandir, Rishabhdeo, Udaipur, Rajasthan 313802, India";
            const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
            window.open(googleMapsUrl, '_blank');
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Show home section by default
            showSection('home');
            
            // Set minimum date for date inputs to today
            const today = new Date().toISOString().split('T')[0];
            const checkInDate = document.getElementById('checkInDate');
            const checkOutDate = document.getElementById('checkOutDate');
            
            if (checkInDate) {
                checkInDate.min = today;
                checkInDate.addEventListener('change', function() {
                    if (checkOutDate) {
                        const nextDay = new Date(this.value);
                        nextDay.setDate(nextDay.getDate() + 1);
                        checkOutDate.min = nextDay.toISOString().split('T')[0];
                    }
                });
            }
            
            if (checkOutDate) {
                checkOutDate.min = today;
            }
            
            // Initialize back to top button
            document.getElementById('backToTop').style.display = 'none';
            
            // Add parallax effect to header
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const header = document.querySelector('.temple-header');
                if (header) {
                    header.style.transform = `translateY(${scrolled * 0.3}px)`;
                }
            });
            
            // Add hover effects to cards
            document.querySelectorAll('.temple-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-10px) rotateX(5deg)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) rotateX(0)';
                });
            });
            
            // Add click effect to buttons
            document.querySelectorAll('.btn-temple-primary').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    // Create ripple effect
                    const ripple = document.createElement('span');
                    const rect = this.getBoundingClientRect();
                    const size = Math.max(rect.width, rect.height);
                    const x = e.clientX - rect.left - size / 2;
                    const y = e.clientY - rect.top - size / 2;
                    
                    ripple.style.cssText = `
                        position: absolute;
                        width: ${size}px;
                        height: ${size}px;
                        left: ${x}px;
                        top: ${y}px;
                        background: rgba(255,255,255,0.3);
                        border-radius: 50%;
                        transform: scale(0);
                        animation: ripple 0.6s linear;
                        pointer-events: none;
                    `;
                    
                    this.style.position = 'relative';
                    this.style.overflow = 'hidden';
                    this.appendChild(ripple);
                    
                    setTimeout(() => ripple.remove(), 600);
                });
            });
            
            // Welcome message
            // setTimeout(() => {
            //     showAlert('🙏 Welcome to our sacred temple! Feel free to explore and contact us for any assistance.', 'success');
            // }, 2000);
        });

        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            .floating-icon {
                animation: float 3s ease-in-out infinite;
            }
            
            /* Enhanced responsive design */
            @media (max-width: 768px) {
                .temple-header h1 {
                    font-size: 1.8rem;
                    line-height: 1.3;
                }
                
                .temple-header h2 {
                    font-size: 1rem;
                }
                
                .section-title {
                    font-size: 1.5rem;
                    margin-bottom: 2rem;
                }
                
                .contact-card {
                    margin-bottom: 1rem;
                }
                
                .temple-slider .carousel-item {
                    height: 50vh;
                }
                
                .btn-temple-primary {
                    padding: 0.8rem 1.5rem;
                    font-size: 0.95rem;
                }
                
                .gallery-item {
                    padding: 1.5rem;
                }
                
                .temple-card {
                    margin-bottom: 1.5rem;
                }
                
                .row.g-4 {
                    --bs-gutter-x: 1rem;
                    --bs-gutter-y: 1rem;
                }
            }
            
            @media (max-width: 576px) {
                .temple-header {
                    padding: 1rem 0;
                }
                
                .temple-header h1 {
                    font-size: 1.5rem;
                }
                
                .temple-header h2 {
                    font-size: 0.9rem;
                }
                
                .temple-slider .carousel-item {
                    height: 40vh;
                    min-height: 250px;
                }
                
                .contact-card {
                    padding: 1rem;
                }
                
                .btn-temple-primary {
                    padding: 0.7rem 1.2rem;
                    font-size: 0.9rem;
                }
                
                .section-title {
                    font-size: 1.5rem;
                }
                
                .card-body.p-5 {
                    padding: 1.5rem !important;
                }
                
                .temple-footer .container {
                    padding: 2rem 1rem;
                }
                
                .floating-alert {
                    right: 10px !important;
                    left: 10px !important;
                    max-width: none !important;
                }
            }
            
            /* Ultra-small screens */
            @media (max-width: 360px) {
                .temple-header h1 {
                    font-size: 1.3rem;
                }
                
                .section-title {
                    font-size: 1.2rem;
                }
                
                .btn-temple-primary {
                    padding: 0.6rem 1rem;
                    font-size: 0.85rem;
                }
                
                .temple-slider .carousel-item {
                    height: 35vh;
                    min-height: 200px;
                }
            }
            
            /* Print styles */
            @media print {
                .navbar, .temple-marquee, .floating-alert, #backToTop, .modal {
                    display: none !important;
                }
                
                .temple-header {
                    background: white !important;
                    color: black !important;
                }
                
                .temple-card {
                    box-shadow: none !important;
                    border: 1px solid #ddd !important;
                }
            }
        `;
        document.head.appendChild(style);

        // Add service worker for offline functionality (optional)
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                // Uncomment below lines if you want to add service worker
                // navigator.serviceWorker.register('/sw.js')
                //     .then(registration => console.log('SW registered'))
                //     .catch(error => console.log('SW registration failed'));
            });
        }

        // Add keyboard navigation
        document.addEventListener('keydown', function(e) {
            // Press 'H' to go to home
            if (e.key === 'h' || e.key === 'H') {
                if (!e.target.matches('input, textarea')) {
                    showSection('home');
                }
            }
            
            // Press 'C' to go to contact
            if (e.key === 'c' || e.key === 'C') {
                if (!e.target.matches('input, textarea')) {
                    showSection('contact');
                }
            }
            
            // Press 'B' to go to booking
            if (e.key === 'b' || e.key === 'B') {
                if (!e.target.matches('input, textarea')) {
                    showSection('booking');
                }
            }
            
            // Press Escape to close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal.show');
                modals.forEach(modal => {
                    bootstrap.Modal.getInstance(modal)?.hide();
                });
            }
        });

        // Add accessibility improvements
        document.querySelectorAll('img').forEach(img => {
            if (!img.alt) {
                img.alt = 'Temple image';
            }
        });

        // Add focus management for better accessibility
    document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');

    // Remove active class
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Add focus/blur listeners
    navLinks.forEach(link => {
        link.addEventListener('focus', function() {
            this.style.outline = '2px solid #FB8B24';
            this.style.outlineOffset = '2px';
        });
        
        link.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });
});
