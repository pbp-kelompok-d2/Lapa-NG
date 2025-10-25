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


// --- List of Hero Images  ---
const heroImages = [
    '/static/images/封面-3.jpg',       // Stadium (main)
    '/static/images/basketball.jpeg', // Basketball
    '/static/images/convert.webp',    // Soccer Action
    '/static/images/skate.png',       // Skateboarding
    '/static/images/GettyImages-1272468011.jpg' // Tennis 
];
let currentImageIndex = 0;

// Preload hero images
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
        getEditForm: scriptData.dataset.getEditFormUrlTemplate,
        getDeleteForm: scriptData.dataset.getDeleteFormUrlTemplate // URL untuk konfirmasi delete
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
    const heroSliderTrack = document.getElementById('hero-slider-track');
    const heroSlides = document.querySelectorAll('.hero-slide');
    const heroDotsContainer = document.getElementById('hero-dots');
    const heroWelcome = document.getElementById('hero-welcome');
    const heroSlogan = document.getElementById('hero-slogan');
    const heroRevealBtn = document.getElementById('hero-reveal-btn');
    const contentWrapper = document.getElementById('content-wrapper');
    const mainNavbar = document.getElementById('main-navbar');
    const heroBg = document.getElementById('hero-bg'); // For parallax
    let heroDots = [];
    let heroInterval;

    // Pagination Container
    const paginationContainer = document.getElementById('pagination-container');

    // Cursor Tooltip Elements
    const cursorTooltip = document.getElementById('cursor-tooltip');
    const cursorTooltipWrapper = document.getElementById('cursor-tooltip-wrapper'); 
    const cursorTooltipContent = document.getElementById('cursor-tooltip'); 
    

    // --- Modal Functions ---
    function openModal() {
        if (modal) modal.classList.remove('hidden');
    }
    function closeModal() {
        if (modal) modal.classList.add('hidden');
        if (modalPanel) modalPanel.innerHTML = ''; // Kosongkan modal saat ditutup
    }


    // --- CURSOR TOOLTIP LOGIC ---
   if (modalPanel && cursorTooltipWrapper && cursorTooltipContent) { // Check for both wrapper and content
        let tooltipVisible = false;

        // Show tooltip pas hover pas di button yang disabled (belum login)
        modalPanel.addEventListener('mouseover', function(event) {
            const targetSpan = event.target.closest('#disabled-add-to-booking-indicator');
            if (targetSpan) {
                cursorTooltipContent.textContent = "Please log in to add to booking"; 
                cursorTooltipWrapper.style.display = 'block'; 
                
                requestAnimationFrame(() => {
                    cursorTooltipWrapper.classList.remove('tooltip-hidden');
                    cursorTooltipWrapper.classList.add('tooltip-visible');
                });
                tooltipVisible = true;
                positionTooltip(event); 
            }
        });

        // Move tooltip with cursor
        modalPanel.addEventListener('mousemove', function(event) {
            if (tooltipVisible) {
                const targetSpan = event.target.closest('#disabled-add-to-booking-indicator');
                if (targetSpan) {
                    positionTooltip(event);
                } else {
                    hideTooltip();
                }
            }
        });

        // Hide tooltip on mouse out
        modalPanel.addEventListener('mouseout', function(event) {
            const targetSpan = event.target.closest('#disabled-add-to-booking-indicator');
            if (targetSpan && !targetSpan.contains(event.relatedTarget)) {
                 hideTooltip();
            } else if (!targetSpan && tooltipVisible) {
                 hideTooltip();
            }
        });

        // Helper function to position the tooltip WRAPPER
        function positionTooltip(e) {
            const offsetX = 10;
            const offsetY = 15;
            let x = e.clientX + offsetX;
            let y = e.clientY + offsetY;

            // Prevent tooltip from going off-screen (using wrapper's dimensions)
            if (x + cursorTooltipWrapper.offsetWidth > window.innerWidth) {
                x = e.clientX - cursorTooltipWrapper.offsetWidth - offsetX;
            }
            if (y + cursorTooltipWrapper.offsetHeight > window.innerHeight) {
                y = e.clientY - cursorTooltipWrapper.offsetHeight - offsetY;
            }
            if (x < 0) x = offsetX;
            if (y < 0) y = offsetY;

            cursorTooltipWrapper.style.left = `${x}px`;
            cursorTooltipWrapper.style.top = `${y}px`;
        }

         // Helper function to hide the tooltip WRAPPER
        function hideTooltip() {
             tooltipVisible = false;
             cursorTooltipWrapper.classList.remove('tooltip-visible');
             cursorTooltipWrapper.classList.add('tooltip-hidden');
             setTimeout(() => {
                 if (!tooltipVisible) { 
                    cursorTooltipWrapper.style.display = 'none';
                 }
             }, 150); 
        }
    }
    // --- END CURSOR TOOLTIP LOGIC ---

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
        if (heroDotsContainer) { // Cek jika elemen ada
            heroImages.forEach((_, index) => {
                const dot = document.createElement('button');
                dot.classList.add('hero-dot', 'w-1', 'h-1', 'rounded-full', 'bg-white', 'bg-opacity-50', 'transition-all');
                dot.dataset.index = index;
                if (index === 0) dot.classList.add('bg-opacity-100', 'scale-125'); // Active state
                heroDotsContainer.appendChild(dot);
                heroDots.push(dot);
            });
        }

        // --- Function to Go To a Specific Slide ---
        function goToSlide(index) {
            if (index < 0 || index >= heroImages.length) return;
            if (!heroSliderTrack) return; // Cek jika elemen ada

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
        heroInterval = setInterval(autoSlide, 5000);

        // --- Add Click Listeners to Dots ---
        if (heroDotsContainer) {
            heroDotsContainer.addEventListener('click', (e) => {
                 if (e.target.classList.contains('hero-dot')) {
                     const index = parseInt(e.target.dataset.index, 10);
                     goToSlide(index);
                     // Reset interval
                     clearInterval(heroInterval);
                     heroInterval = setInterval(autoSlide, 10000);
                 }
             });
         }

        // --- Initial Navbar State (Hidden) ---
        if (mainNavbar) {
            mainNavbar.classList.add('opacity-0', '-translate-y-full', 'pointer-events-none');
        }
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

                if (mainNavbar) mainNavbar.classList.remove('opacity-0', '-translate-y-full', 'pointer-events-none');
                heroSection.classList.remove('fixed', 'inset-0', 'h-screen');
                heroSection.classList.add('relative');
                heroSection.style.height = '60vh';
                contentWrapper.classList.remove('mt-[100vh]');
                contentWrapper.classList.add('mt-0');
                if (heroRevealBtn) heroRevealBtn.classList.add('opacity-0');
            }
        }

        // --- Function to RESET to full hero ---
        function resetToFullHero() {
             if (!isHeroFull) {
                 console.log("Resetting to full hero");
                 isHeroFull = true;

                 if (mainNavbar) mainNavbar.classList.add('opacity-0', '-translate-y-full', 'pointer-events-none');
                 heroSection.classList.add('fixed', 'inset-0', 'h-screen');
                 heroSection.classList.remove('relative');
                 heroSection.style.height = '';
                 contentWrapper.classList.add('mt-[100vh]');
                 contentWrapper.classList.remove('mt-0');
                 if (heroRevealBtn) {
                     heroRevealBtn.classList.add('opacity-0');
                     requestAnimationFrame(() => {
                        heroRevealBtn.classList.remove('opacity-0');
                     });
                 }
             }
         }

        // --- Button Click ---
        if (heroRevealBtn) {
            heroRevealBtn.addEventListener('click', function onHeroRevealClick() {
                if (!isHeroFull) return;
                heroRevealBtn.disabled = true;
                console.log('Revealing content (unified handler)');
                revealContent();
                isScrollingProgrammatically = true;
                requestAnimationFrame(() => {
                    setTimeout(() => {
                        const NUDGE_PX = 120;
                        window.scrollBy({ top: NUDGE_PX, behavior: 'smooth' });
                        setTimeout(() => {
                            isScrollingProgrammatically = false;
                            heroRevealBtn.disabled = false;
                        }, 700);
                    }, 120);
                });
            });
        }

        // --- Scroll Listener ---
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (isScrollingProgrammatically) {
                console.log("Scroll event ignored (programmatic)");
                return;
            }
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                if (isScrollingProgrammatically) return;
                const scrollPosition = window.scrollY;
                console.log("Manual Scroll Detected:", scrollPosition);

                if (isHeroFull && scrollPosition > 50) {
                    revealContent();
                } else if (!isHeroFull && scrollPosition === 0) {
                    resetToFullHero();
                }

                if (heroRevealBtn && !isHeroFull && scrollPosition > 100) {
                     heroRevealBtn.classList.add('opacity-0');
                }
            }, 50);
        });

        // --- Mouse Parallax Listener ---
        if (heroBg) { // Cek jika elemen parallax ada
            heroSection.addEventListener('mousemove', (e) => {
                if (!isHeroFull) {
                    const { clientX, clientY } = e;
                    const { offsetWidth, offsetHeight } = heroSection;
                    const xPercent = (clientX / offsetWidth) - 0.5;
                    const yPercent = (clientY / offsetHeight) - 0.5;
                    const intensity = 15;
                    const moveX = xPercent * intensity * -1;
                    const moveY = yPercent * intensity * -1;
                    heroBg.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.1)`;
                }
            });
            heroSection.addEventListener('mouseleave', () => {
                 if (!isHeroFull) {
                     heroBg.style.transform = `translate(0, 0) scale(1.1)`;
                 }
             });
         }
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
                .then(response => response.json()) 
                .then(data => {                  
                    if (venueContainer) venueContainer.innerHTML = data.list_html;
                    if (paginationContainer) paginationContainer.innerHTML = data.pagination_html; // <-- ADD THIS
                    history.pushState(null, '', `${URLS.showMain}?${params.toString()}`);
                })
                .catch(error => {
                    console.error('Filter error:', error);
                    if (venueContainer) venueContainer.innerHTML = '<p class="text-center text-red-600">Error loading venues.</p>';
                 });
        });
    }

    // --- LISTENER BARU UNTUK PAGINATION (AJAX) ---
    if (contentWrapper) {
        contentWrapper.addEventListener('click', function(event) {
            const pageLink = event.target.closest('.page-link'); // Target semua link di pagination
            
            if (pageLink && pageLink.tagName === 'A') { // Pastikan itu link, bukan span
                event.preventDefault(); // Stop reload halaman
                const fetchUrl = pageLink.href;
                
                // Ambil URL lengkap dan ekstrak query string
                const queryString = fetchUrl.split('?')[1] || '';
                const ajaxUrl = `${URLS.filter}?${queryString}`;
                const browserUrl = `${URLS.showMain}?${queryString}`;

                fetch(ajaxUrl)
                    .then(response => response.json())
                    .then(data => {
                        if (venueContainer) venueContainer.innerHTML = data.list_html;
                        if (paginationContainer) paginationContainer.innerHTML = data.pagination_html;
                        
                        // Update URL di browser
                        history.pushState(null, '', browserUrl);
                        
                        // Scroll ke atas list
                        contentWrapper.scrollIntoView({ behavior: 'smooth' });
                    })
                    .catch(error => {
                        console.error('Pagination error:', error);
                        showToast('Could not load page.', 'error');
                    });
            }
        });
    }

    // --- Clear Filter Button Logic ---
    const clearButton = document.getElementById('clear-filter-btn');
    if (clearButton) {
        clearButton.addEventListener('click', function(event) {
            event.preventDefault();
            fetch(URLS.filter)
                .then(response => response.json()) 
                .then(data => {                   
                    if (venueContainer) venueContainer.innerHTML = data.list_html;
                    if (paginationContainer) paginationContainer.innerHTML = data.pagination_html; 
                    if (filterForm) filterForm.reset();
                    history.pushState(null, '', URLS.showMain);
                })
                .catch(error => {
                    console.error('Error fetching unfiltered venues:', error);
                    if (venueContainer) venueContainer.innerHTML = '<p class="text-center text-red-600">Error loading venues.</p>';
                });
        });
    }

    // --- "VIEW VENUE" MODAL (Card Click) ---
    if (venueContainer) {
        venueContainer.addEventListener('click', function(event) {
            const card = event.target.closest('.venue-card');
            if (card && card.dataset.slug) {
                const slug = card.dataset.slug;
                const fetchUrl = URLS.venueDetail.replace('SLUG_PLACEHOLDER', slug);
                fetch(fetchUrl)
                    .then(response => { if (!response.ok) throw new Error('Network response not ok'); return response.text(); })
                    .then(html => {
                        if (modalPanel) modalPanel.innerHTML = html;
                        openModal();
                     })
                    .catch(error => {
                        console.error("View Venue Error:", error);
                        showToast('Could not load venue details.', 'error');
                     });
            }
        });
    }

    // --- "CREATE VENUE" MODAL (Button Click) ---
    if (addVenueBtn) {
        addVenueBtn.addEventListener('click', function() {
            fetch(URLS.getCreateForm)
                .then(response => {
                    if (response.status === 403) {
                        showToast('Please login to add a venue.', 'error');
                        // Opsional: Redirect ke login
                        // window.location.href = '/auth/login/';
                        return Promise.reject('Forbidden');
                    }
                    if (!response.ok) throw new Error('Could not load create form.');
                    return response.json();
                 })
                .then(data => {
                    if (modalPanel) modalPanel.innerHTML = data.html;
                    openModal();
                 })
                .catch(error => {
                    if (error !== 'Forbidden') { // Jangan tampilkan toast jika hanya masalah login
                       console.error("Create Venue Load Error:", error);
                       showToast('Could not open the add venue form.', 'error');
                    }
                 });
        });
    }

    // --- COMBINED MODAL BUTTON CLICK HANDLER (Edit, Delete, Add to Booking, Close) ---
    if (modalPanel) {
        // Helper CSRF
        function getCSRFToken() {
            const name = 'csrftoken=';
            const parts = document.cookie.split(';').map(s => s.trim());
            for (const p of parts) {
                if (p.startsWith(name)) return p.substring(name.length);
            }
            return null;
        }

        modalPanel.addEventListener('click', function(event) {
            // Close Button
            if (event.target.closest('#modal-close-btn')) {
                closeModal();
                return;
            }

            // --- Add to Booking ---
            const bookingBtn = event.target.closest('#add-to-booking-btn');
            if (bookingBtn) {
                const venueId = bookingBtn.dataset.venueId || bookingBtn.getAttribute('data-venue-id');
                if (!venueId) {
                    showToast('Venue ID not found for booking.', 'error');
                    return;
                }
                const url = URLS.bookingAdd.replace('0', venueId);

                const csrftoken = getCSRFToken();
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken || '',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    }
                })
                .then(res => res.json()) 
                .then(data => {
                    if (data.status === 'ok') {
                        showToast(data.message || 'Added to booking.', 'success');
                         if (URLS.bookingRedirect) window.location.href = URLS.bookingRedirect;
                         else closeModal(); 
                    } else {
                        throw new Error(data.message || 'Failed to add to booking');
                    }
                })
                .catch(err => {
                    console.error('Booking add error:', err);
                    showToast(err.message || 'Could not add to booking.', 'error');
                });
                return;
            }

            // --- Edit Venue (load edit form into modal) ---
            const editBtn = event.target.closest('#edit-venue-btn');
            if (editBtn) {
                const slug = editBtn.dataset.slug;
                if (!slug || !URLS.getEditForm) { showToast('Cannot load edit form.', 'error'); return; }
                const fetchUrl = URLS.getEditForm.replace('SLUG_PLACEHOLDER', slug);
                fetch(fetchUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(res => { if (!res.ok) throw new Error('Could not load edit form'); return res.json(); })
                    .then(data => {
                        if (data.html) {
                            modalPanel.innerHTML = data.html;
                            openModal(); 
                        } else { throw new Error('Edit form unavailable.'); }
                    })
                    .catch(err => { console.error('Load edit form error:', err); showToast(err.message, 'error'); });
                return;
            }

            // --- Delete Venue (load delete confirmation into modal) ---
            const deleteBtn = event.target.closest('#delete-venue-btn');
            if (deleteBtn) {
                const slug = deleteBtn.dataset.slug;
                if (!slug || !URLS.getDeleteForm) { showToast('Cannot load delete confirmation.', 'error'); return; }
                const fetchUrl = URLS.getDeleteForm.replace('SLUG_PLACEHOLDER', slug);
                fetch(fetchUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(res => { if (!res.ok) throw new Error('Could not load delete confirmation'); return res.json(); })
                    .then(data => {
                        if (data.html) {
                            modalPanel.innerHTML = data.html;
                            openModal(); 
                        } else { throw new Error('Delete confirmation unavailable.'); }
                    })
                    .catch(err => { console.error('Load delete form error:', err); showToast(err.message, 'error'); });
                return;
            }
        }); // --- Akhir dari modalPanel 'click' listener ---
    } // --- Akhir dari if (modalPanel) ---


    // --- MODAL FORM SUBMISSION HANDLER (Create, Edit, Delete Confirmation) ---
    if (modalPanel) {
        modalPanel.addEventListener('submit', function(event) {

            // --- Logika untuk form CREATE dan EDIT ---
            if (event.target.id === 'venue-form') {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const originalSlug = form.querySelector('#venue-slug-for-update')?.value;
                const csrfToken = formData.get('csrfmiddlewaretoken');
                if (!csrfToken) { showToast('CSRF Token missing.', 'error'); return; }

                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': csrfToken, 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => {
                    // Cek jika response adalah JSON, jika tidak, reject dengan text
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json().then(data => ({ ok: response.ok, status: response.status, data }));
                    }
                    return response.text().then(text => Promise.reject(new Error(`Server response was not JSON: ${text}`)));
                })
                .then(({ ok, status, data }) => {
                    if (ok && data.status === 'ok') {
                        closeModal();
                        showToast(data.message, 'success');
                        if (originalSlug && data.updated_card_html) { // Edit success
                            const originalCard = venueContainer.querySelector(`.venue-card[data-slug="${originalSlug}"]`);
                            if (originalCard) originalCard.outerHTML = data.updated_card_html;
                            else if (filterForm) filterForm.dispatchEvent(new Event('submit', { cancelable: true })); // Reload list jika card tidak ditemukan
                        } else if (data.new_card_html) { // Create success
                           if (venueContainer) {
                               const grid = venueContainer.querySelector('.grid');
                               if (grid) grid.insertAdjacentHTML('afterbegin', data.new_card_html);
                           }
                        }
                    } else if (!ok && data.form_html) { // Validation error from backend
                        modalPanel.innerHTML = data.form_html; // Re-render form with errors
                    } else { // Error lain dari backend
                       throw new Error(data.message || `Server error: ${status}`);
                    }
                })
                .catch(error => {
                     console.error('Form submission error:', error);
                     // Jangan re-render jika bukan error validasi form
                     if (!modalPanel.innerHTML.includes(error.form_html)) {
                        showToast(error.message || 'An error occurred during submission.', 'error');
                     }
                });
            }

            // --- Logika untuk form DELETE Confirmation ---
            else if (event.target.id === 'delete-venue-form') {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const csrfToken = formData.get('csrfmiddlewaretoken');
                if (!csrfToken) { showToast('CSRF Token missing.', 'error'); return; }

                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken || '',
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json()) // Asumsikan delete selalu return JSON
                .then(data => {
                    if (data.status === 'ok') {
                        closeModal();
                        showToast(data.message, 'success');
                        if (data.deleted_slug && venueContainer) {
                            const card = venueContainer.querySelector(`.venue-card[data-slug="${data.deleted_slug}"]`);
                            if (card) card.remove();
                        }
                    } else {
                       throw new Error(data.message || 'Deletion failed.');
                    }
                })
                .catch(error => {
                    console.error('Delete submission error:', error);
                    showToast(error.message || 'Could not delete venue.', 'error');
                });
            }

        }); // <-- Akhir dari addEventListener 'submit'
    } // <-- Akhir dari if (modalPanel)

    // --- Close modal on overlay click ---
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }

}); // <-- Akhir dari DOMContentLoaded