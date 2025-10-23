// ---  TOAST FUNCTION ---
/**
 * Displays a toast notification.
 * @param {string} message The message to display.
 * @param {string} type 'success', 'error', or 'info'
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Create the toast element
    const toast = document.createElement('div');
    toast.className = `p-4 rounded-lg shadow-lg text-white font-medium transition-all duration-300 transform translate-x-full`;
    toast.innerText = message;

    // Set color based on type
    if (type === 'success') {
        toast.classList.add('bg-green-600');
    } else if (type === 'error') {
        toast.classList.add('bg-red-600');
    } else {
        toast.classList.add('bg-blue-600');
    }

    // Add to container
    container.appendChild(toast);

    // --- Animate in ---
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);

    // --- Animate out and remove ---
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-full');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }, 3000); // Toast visible for 3 seconds
}

// --- List of Hero Images (Define outside DOMContentLoaded) ---
const heroImages = [
    '/static/images/封面-3.jpg',       // Stadium (FIRST) - Make sure filename is correct
    '/static/images/basketball.jpeg', // Basketball
    '/static/images/convert.webp',    // Soccer Action
    '/static/images/skate.png',       // Skateboarding
    '/static/images/GettyImages-1272468011.jpg' // Tennis Serve
];
let currentImageIndex = 0;

heroImages.forEach(src => {
    const img = new Image();
    img.src = src;
});

document.addEventListener('DOMContentLoaded', function() {

    // --- 1. READ URLS ---
    const scriptData = document.getElementById('main-script-data');
    const URLS = {
        filter: scriptData.dataset.filterUrl,
        showMain: scriptData.dataset.showMainUrl,
        venueDetail: scriptData.dataset.venueDetailUrlTemplate,
        bookingAdd: scriptData.dataset.bookingAddUrlTemplate,
        bookingRedirect: scriptData.dataset.bookingRedirectUrl,
        getCreateForm: scriptData.dataset.getCreateFormUrl,
        getEditForm: scriptData.dataset.getEditFormUrlTemplate
        // Note: Delete URL is constructed dynamically
    };

    // --- DOM Elements ---
    const filterForm = document.getElementById('filter-form');
    const venueContainer = document.getElementById('venue-list-container');
    const modal = document.getElementById('main-modal');
    const modalPanel = document.getElementById('modal-panel');
    const modalOverlay = document.getElementById('modal-overlay');
    const addVenueBtn = document.getElementById('add-venue-btn');

    // Hero Elements
    const heroSection = document.getElementById('hero-section');
    const heroSliderTrack = document.getElementById('hero-slider-track'); // New
    const heroSlides = document.querySelectorAll('.hero-slide'); // New
    const heroDotsContainer = document.getElementById('hero-dots'); // New
    const heroWelcome = document.getElementById('hero-welcome');
    const heroSlogan = document.getElementById('hero-slogan');
    const heroRevealBtn = document.getElementById('hero-reveal-btn');
    const contentWrapper = document.getElementById('content-wrapper'); 
    const mainNavbar = document.getElementById('main-navbar');   
    const heroBg = document.getElementById('hero-bg'); // For parallax
    let heroDots = []; // To store dot elements
    let heroInterval; // To store the interval ID

    // --- Modal Functions ---
    function openModal() {
        if(modal) modal.classList.remove('hidden');
    }
    function closeModal() {
        if(modal) modal.classList.add('hidden');
        if(modalPanel) modalPanel.innerHTML = '';
    }

    // ===================================
    // ===== HERO SECTION LOGIC ========
    // ===================================
    let isHeroFull = true; 
    let isScrollingProgrammatically = false;

    if (heroSection && contentWrapper && mainNavbar && heroSliderTrack && heroSlides.length > 0) {
        
        // --- Set Initial Slide Backgrounds ---
        heroSlides.forEach((slide, index) => {
             if (heroImages[index]) {
                 slide.style.backgroundImage = `url('${heroImages[index]}')`;
             }
        });

        // --- Generate Dots ---
        heroImages.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.classList.add('hero-dot', 'w-1', 'h-1', 'rounded-full', 'bg-white', 'bg-opacity-50', 'transition-all');
            dot.dataset.index = index;
            if (index === 0) dot.classList.add('bg-opacity-50', 'scale-125'); // Active state
            heroDotsContainer.appendChild(dot);
            heroDots.push(dot); // Store dot element
        });

        // --- Function to Go To a Specific Slide ---
        function goToSlide(index) {
            if (index < 0 || index >= heroImages.length) return; // Boundary check
            
            heroSliderTrack.style.transform = `translateX(-${index * 100}%)`;
            currentImageIndex = index;

            // Update active dot
            heroDots.forEach((dot, i) => {
                if (i === index) {
                    dot.classList.add('bg-opacity-100', 'scale-125');
                } else {
                    dot.classList.remove('bg-opacity-100', 'scale-125');
                }
            });
        }
        
        // --- Auto-Slide Function ---
        function autoSlide() {
             let nextIndex = (currentImageIndex + 1) % heroImages.length;
             goToSlide(nextIndex);
        }

        // --- Start Auto-Sliding ---
        heroInterval = setInterval(autoSlide, 5000); // Change every 5 seconds

        // --- Add Click Listeners to Dots ---
         heroDotsContainer.addEventListener('click', (e) => {
             if (e.target.classList.contains('hero-dot')) {
                 const index = parseInt(e.target.dataset.index, 10);
                 goToSlide(index);
                 // Reset interval after manual click
                 clearInterval(heroInterval);
                 heroInterval = setInterval(autoSlide, 10000);
             }
         });

        // --- Initial Navbar State (Hidden) ---
        mainNavbar.classList.add('opacity-0', '-translate-y-full', 'pointer-events-none');
        // --- Initial Text/Button Fade-In Animations ---
        requestAnimationFrame(() => {
            if (heroWelcome) heroWelcome.classList.remove('opacity-0');
            if (heroSlogan) heroSlogan.classList.remove('opacity-0');
            if (heroRevealBtn) heroRevealBtn.classList.remove('opacity-0');
        });

        // --- Function to REVEAL content ---
        function revealContent() {
            if (isHeroFull) {
                console.log("Revealing content");
                isHeroFull = false;

                // 1. Show Navbar smoothly
                mainNavbar.classList.remove('opacity-0', '-translate-y-full', 'pointer-events-none');

                // 2. Change Hero: Fixed -> Relative, adjust height
                heroSection.classList.remove('fixed', 'inset-0', 'h-screen');
                heroSection.classList.add('relative');
                heroSection.style.height = '60vh'; // Smaller height

                // 3. Bring content wrapper up
                contentWrapper.classList.remove('mt-[100vh]');
                contentWrapper.classList.add('mt-0');

                // 4. Fade out button (redundant due to scroll listener, but ensures it happens)
                if (heroRevealBtn) heroRevealBtn.classList.add('opacity-0');
            }
        }

        // --- Function to RESET to full hero ---
        function resetToFullHero() {
             if (!isHeroFull) {
                 console.log("Resetting to full hero");
                 isHeroFull = true;

                 // Hide Navbar
                 mainNavbar.classList.add('opacity-0', '-translate-y-full', 'pointer-events-none');

                 // Reset Hero: Relative -> Fixed, full height
                 heroSection.classList.add('fixed', 'inset-0', 'h-screen');
                 heroSection.classList.remove('relative');
                 heroSection.style.height = ''; // Reset height style

                 // Push content wrapper back down
                 contentWrapper.classList.add('mt-[100vh]');
                 contentWrapper.classList.remove('mt-0');

                 // Re-show button (initial fade-in logic will handle the animation via requestAnimationFrame)
                 if (heroRevealBtn) {
                     // Need to re-trigger the fade-in if we reset
                     heroRevealBtn.classList.add('opacity-0'); // Ensure it starts hidden
                     requestAnimationFrame(() => { // Then fade it in
                        heroRevealBtn.classList.remove('opacity-0');
                     });
                 }
             }
         }

        // --- Button Click ---
      if (heroRevealBtn) {
            // Unified single handler: reveal and small nudge only.
            heroRevealBtn.addEventListener('click', function onHeroRevealClick() {
                // Only act when hero is still full
                if (!isHeroFull) return;

                // Prevent double clicks while animating
                heroRevealBtn.disabled = true;

                console.log('Revealing content (unified handler)');
                revealContent();

                // Prevent scroll listener from reacting to our programmatic move
                isScrollingProgrammatically = true;

                // Small nudge after paint so CSS transitions start
                requestAnimationFrame(() => {
                    setTimeout(() => {
                        const NUDGE_PX = 120;
                        window.scrollBy({ top: NUDGE_PX, behavior: 'smooth' });

                        // Re-enable listeners and button after the smooth scroll finishes
                        setTimeout(() => {
                            isScrollingProgrammatically = false;
                            heroRevealBtn.disabled = false;
                        }, 700);
                    }, 120);
                });
            });
        }

        // --- Scroll Listener (Simplified Flag Check) ---
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            // --- Check flag immediately ---
            if (isScrollingProgrammatically) {
                console.log("Scroll event ignored (programmatic)");
                return; // Ignore scroll events triggered by our button click
            }
            // --- End Check ---

            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                // Re-check flag just in case state changed during timeout
                if (isScrollingProgrammatically) return;

                const scrollPosition = window.scrollY;
                console.log("Manual Scroll Detected:", scrollPosition); // Debugging

                if (isHeroFull && scrollPosition > 50) {
                    revealContent();
                } else if (!isHeroFull && scrollPosition === 0) {
                    // Only reset if truly at the top after manual scroll
                    resetToFullHero();
                }

                // Fade button out logic remains
                if (heroRevealBtn && !isHeroFull) {
                     if (scrollPosition > 100) {
                          heroRevealBtn.classList.add('opacity-0');
                     }
                }
            }, 50); // Shorter debounce for responsiveness
        });

        // --- Mouse Parallax Listener ---
        heroSection.addEventListener('mousemove', (e) => {
            if (!isHeroFull && heroBg) { // Apply only when revealed
                const { clientX, clientY } = e;
                const { offsetWidth, offsetHeight } = heroSection;
                const xPercent = (clientX / offsetWidth) - 0.5;
                const yPercent = (clientY / offsetHeight) - 0.5;
                const intensity = 15;
                const moveX = xPercent * intensity * -1; // Invert X for natural feel
                const moveY = yPercent * intensity * -1; // Invert Y for natural feel
                heroBg.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.1)`;
            }
        });
        // Reset parallax slightly on mouse leave
         heroSection.addEventListener('mouseleave', () => {
             if(!isHeroFull && heroBg) {
                 heroBg.style.transform = `translate(0, 0) scale(1.1)`;
             }
         });

    }
    // ===================================
    // === END HERO SECTION LOGIC ======
    // ===================================

    // --- AJAX FILTER LOGIC ---
    if (filterForm) {
        filterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(filterForm);
            const params = new URLSearchParams(formData);
            fetch(`${URLS.filter}?${params.toString()}`)
                .then(response => response.text())
                .then(html => {
                    venueContainer.innerHTML = html;
                    history.pushState(null, '', `?${params.toString()}`);
                })
                .catch(error => { /* ... error handling ... */ });
        });
    }
    const clearButton = document.querySelector(`a[href="${URLS.showMain}"]`);
    if (clearButton) { /* ... clear button logic ... */ }

    // --- "VIEW VENUE" MODAL (Card Click) ---
    if (venueContainer) {
        venueContainer.addEventListener('click', function(event) {
            const card = event.target.closest('.venue-card');
            if (card) {
                const slug = card.dataset.slug;
                if (!slug) return;
                const fetchUrl = URLS.venueDetail.replace('SLUG_PLACEHOLDER', slug);
                fetch(fetchUrl)
                    .then(response => { if (!response.ok) throw new Error('Network response not ok'); return response.text(); })
                    .then(html => { modalPanel.innerHTML = html; openModal(); })
                    .catch(error => { /* ... error handling ... */ });
            }
        });
    }

    // --- "CREATE VENUE" MODAL (Button Click) ---
    if (addVenueBtn) {
        addVenueBtn.addEventListener('click', function() {
            fetch(URLS.getCreateForm)
                .then(response => { if (response.status === 403) { /* ... login redirect ... */; return Promise.reject('Forbidden'); } if (!response.ok) throw new Error('Could not load create form.'); return response.json(); })
                .then(data => { modalPanel.innerHTML = data.html; openModal(); })
                .catch(error => { /* ... error handling ... */ });
        });
    }

    // --- COMBINED MODAL BUTTON CLICK HANDLER ---
    if (modalPanel) {
        modalPanel.addEventListener('click', function(event) {
            // Close Button
            if (event.target.closest('#modal-close-btn')) { closeModal(); return; }
            // Add to Booking Button
            const bookingBtn = event.target.closest('#add-to-booking-btn');
            if (bookingBtn) { /* ... booking logic ... */ return; }
            // Edit Button
            const editBtn = event.target.closest('#edit-venue-btn');
            if (editBtn) { /* ... edit logic ... */ return; }
            // Delete Button
            const deleteBtn = event.target.closest('#delete-venue-btn');
            if (deleteBtn) { /* ... delete logic ... */ return; }
        });
    }

    // --- MODAL FORM SUBMISSION HANDLER ---
    if (modalPanel) {
        modalPanel.addEventListener('submit', function(event) {
            if (event.target.id === 'venue-form') {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const originalSlug = form.querySelector('#venue-slug-for-update')?.value;
                const csrfToken = formData.get('csrfmiddlewaretoken');
                if (!csrfToken) { /* ... error handling ... */ return; }

                fetch(form.action, { method: 'POST', body: formData, headers: { 'X-CSRFToken': csrfToken, 'Accept': 'application/json' } })
                .then(response => { // Add better response checking
                    if (!response.ok && response.headers.get('Content-Type')?.includes('application/json')) {
                         return response.json().then(data => Promise.reject(data)); // Pass error JSON down
                    } else if (!response.ok) {
                         return response.text().then(text => Promise.reject(text)); // Pass HTML error down
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'ok') {
                        closeModal(); showToast(data.message, 'success');
                        if (originalSlug && data.updated_card_html) { // Edit success
                            const originalCard = venueContainer.querySelector(`.venue-card[data-slug="${originalSlug}"]`);
                            if (originalCard) originalCard.outerHTML = data.updated_card_html;
                            else filterForm.dispatchEvent(new Event('submit', { cancelable: true })); // Fallback reload list
                        } else if (data.new_card_html) { // Create success
                            venueContainer.querySelector('.grid').insertAdjacentHTML('afterbegin', data.new_card_html);
                        }
                    }
                    // No need for explicit 'error' status check here if using reject above
                })
                .catch(error => {
                     console.error('Form submission error:', error);
                     if (error.form_html) { // Validation error from backend JSON
                         modalPanel.innerHTML = error.form_html; // Re-render form
                     } else if (typeof error === 'string') { // HTML error response
                         showToast('An unexpected server error occurred.', 'error');
                         // Optionally display 'error' in modal or close it
                     } else { // Network error or other JS error
                        showToast(error.message || 'An error occurred.', 'error');
                     }
                });
            }
            // --- Delete confirmation form (if using modal) ---
            // else if (event.target.id === 'delete-venue-form') { ... }
        });
    }

    // --- Close modal on overlay click ---
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }
});