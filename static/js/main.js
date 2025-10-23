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
    // Short delay to allow element to be added to DOM first
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);

    // --- Animate out and remove ---
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-full');
        // Remove from DOM after animation
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }, 3000); // Toast visible for 3 seconds
}


document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. READ URLS FROM THE TEMPLATE ---
    // Get the <script> tag in main.html that holds our URLs
    const scriptData = document.getElementById('main-script-data');
    const URLS = {
        filter: scriptData.dataset.filterUrl,
        showMain: scriptData.dataset.showMainUrl,
        venueDetail: scriptData.dataset.venueDetailUrlTemplate,
        bookingAdd: scriptData.dataset.bookingAddUrlTemplate,
        bookingRedirect: scriptData.dataset.bookingRedirectUrl,
        getCreateForm: scriptData.dataset.getCreateFormUrl,
    };

    // --- 2. AJAX FILTER LOGIC ---
    const form = document.getElementById('filter-form');
    const venueContainer = document.getElementById('venue-list-container');

    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            const formData = new FormData(form);
            const params = new URLSearchParams(formData);

            // Use the URL from our URLS object
            fetch(`${URLS.filter}?${params.toString()}`)
                .then(response => response.text())
                .then(html => {
                    venueContainer.innerHTML = html;
                    history.pushState(null, '', `?${params.toString()}`);
                })
                .catch(error => {
                    console.error('Error fetching venues:', error);
                    venueContainer.innerHTML = '<p class="text-center text-red-600">Error loading venues. Please try again.</p>';
                });
        });
    }

    // Use the URL from our URLS object
    const clearButton = document.querySelector(`a[href="${URLS.showMain}"]`);
    if (clearButton) {
        clearButton.addEventListener('click', function(event) {
            event.preventDefault();
            // Use the URL from our URLS object
            window.location.href = URLS.showMain; 
        });
    }

    // --- 3. "VIEW VENUE" MODAL LOGIC ---
    const modal = document.getElementById('main-modal');
    const modalPanel = document.getElementById('modal-panel');
    const modalOverlay = document.getElementById('modal-overlay');
    
    function openModal() {
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
        modalPanel.innerHTML = ''; 
    }

    venueContainer.addEventListener('click', function(event) {
        const card = event.target.closest('.venue-card');
        if (card) {
            const slug = card.dataset.slug;
            if (!slug) return;

            // Use the URL template and replace the placeholder
            const fetchUrl = URLS.venueDetail.replace('SLUG_PLACEHOLDER', slug);

            fetch(fetchUrl)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.text();
                })
                .then(html => {
                    modalPanel.innerHTML = html;
                    openModal();
                })
                .catch(error => {
                    console.error('Error fetching venue details:', error);
                    alert('Error loading venue details.');
                });
        }
    });

    // --- 4. "ADD VENUE" MODAL LOGIC ---
    const addVenueBtn = document.getElementById('add-venue-btn');
    if (addVenueBtn) {
        addVenueBtn.addEventListener('click', function() {
            fetch(URLS.getCreateForm)
                .then(response => {
                    if (response.status === 403) {
                        alert('You must be logged in to add a venue.');
                        window.location.href = '/auth/login/';
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    modalPanel.innerHTML = data.html;
                    openModal();
                })
                .catch(error => {
                    console.error('Error fetching create form:', error);
                    showToast('Error loading form.', 'error');
                });
        });
    }


    // --- 5. MODAL BUTTON HANDLERS ---
    modalPanel.addEventListener('click', function(event) {
        
        if (event.target.closest('#modal-close-btn')) {
            closeModal();
            return; 
        }

        // --- add to booking ---
        const bookingBtn = event.target.closest('#add-to-booking-btn');
        if (bookingBtn) {
            const venueId = bookingBtn.dataset.venueId;
            if (!venueId) return;

            // Use the URL template and replace '0' with the real ID
            const fetchUrl = URLS.bookingAdd.replace('0', venueId);

            fetch(fetchUrl)
                .then(response => {
                    if (response.status === 403) {
                        // Handle not being logged in
                        alert('You must be logged in to add a booking.');
                        window.location.href = '/auth/login/'; // Redirect to login
                        return;
                    }
                    if (!response.ok) {
                        throw new Error('Booking request failed');
                    }
                    return response.json();
                })
                .then(data => {
                    // 1. Show success toast
                    showToast(data.message || 'Added to booking!', 'success');
                    
                    // 2. Close the modal
                    closeModal();

                    // 3. Redirect to the booking page after a short delay
                    setTimeout(() => {
                        window.location.href = URLS.bookingRedirect;
                    }, 1000); // 1-second delay so user can see toast
                })
                .catch(error => {
                    console.error('Error adding to booking:', error);
                    showToast('Error: Could not add to booking.', 'error');
                });
        }
    });

    // --- 6. MODAL FORM SUBMISSION LOGIC ---
    modalPanel.addEventListener('submit', function(event) {
        // Check if it's our form that was submitted
        if (event.target.id === 'venue-form') {
            event.preventDefault(); 
            const form = event.target;
            const formData = new FormData(form);

            fetch(form.action, { // form.action is the URL we set in _venue_form.html
                method: 'POST',
                body: formData,
                headers: {
                    // Django's CSRF token
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // SUCCESS!
                    closeModal();
                    showToast(data.message, 'success');
                    // Add the new card to the top of the list
                    venueContainer.querySelector('.grid').insertAdjacentHTML('afterbegin', data.new_card_html);
                } else if (data.status === 'error' && data.form_html) {
                    // Form validation error
                    // Re-render the form inside the modal with error messages
                    modalPanel.innerHTML = data.form_html;
                } else {
                    // Other server error
                    throw new Error(data.message || 'Form submission failed.');
                }
            })
            .catch(error => {
                console.error('Form submission error:', error);
                showToast(error.message, 'error');
            });
        }
    });
    

    modalOverlay.addEventListener('click', closeModal);
});
