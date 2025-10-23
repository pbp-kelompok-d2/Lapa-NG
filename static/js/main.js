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
        // Note: Delete URL is constructed dynamically later
    };

    // --- DOM Elements ---
    const form = document.getElementById('filter-form');
    const venueContainer = document.getElementById('venue-list-container');
    const modal = document.getElementById('main-modal');
    const modalPanel = document.getElementById('modal-panel');
    const modalOverlay = document.getElementById('modal-overlay');
    const addVenueBtn = document.getElementById('add-venue-btn');
    
    // --- Modal Functions ---
    function openModal() {
        modal.classList.remove('hidden');
    }

    function closeModal() {
        modal.classList.add('hidden');
        modalPanel.innerHTML = ''; 
    }

    // --- 2. AJAX FILTER LOGIC ---
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            const formData = new FormData(form);
            const params = new URLSearchParams(formData);

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

    const clearButton = document.querySelector(`a[href="${URLS.showMain}"]`);
    if (clearButton) {
        clearButton.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = URLS.showMain; 
        });
    }

    // --- 3. "VIEW VENUE" MODAL (Card Click) ---
    venueContainer.addEventListener('click', function(event) {
        const card = event.target.closest('.venue-card');
        if (card) {
            const slug = card.dataset.slug;
            if (!slug) return;
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

    // --- 4. "CREATE VENUE" MODAL (Button Click) ---
    if (addVenueBtn) {
        addVenueBtn.addEventListener('click', function() {
            fetch(URLS.getCreateForm)
                .then(response => {
                    if (response.status === 403) {
                        alert('You must be logged in to add a venue.');
                        window.location.href = '/auth/login/';
                        return Promise.reject('Forbidden'); // Stop promise chain
                    }
                    if (!response.ok) throw new Error('Could not load create form.');
                    return response.json();
                })
                .then(data => {
                    modalPanel.innerHTML = data.html;
                    openModal();
                })
                .catch(error => {
                    if (error !== 'Forbidden') { // Avoid double alert
                       console.error('Error fetching create form:', error);
                       showToast('Error loading form.', 'error');
                    }
                });
        });
    }
    
    // --- 5. COMBINED MODAL BUTTON CLICK HANDLER (Event Delegation) ---
    // Handles Close, Edit, Delete, Add-to-Booking clicks *inside* the modal
    modalPanel.addEventListener('click', function(event) {
        
        // Handle Close Button
        if (event.target.closest('#modal-close-btn')) {
            closeModal();
            return; 
        }

        // Handle Add to Booking Button
        const bookingBtn = event.target.closest('#add-to-booking-btn');
        if (bookingBtn) {
            const venueId = bookingBtn.dataset.venueId;
            if (!venueId) return;
            const fetchUrl = URLS.bookingAdd.replace('0', venueId);

            fetch(fetchUrl)
                .then(response => {
                    if (response.status === 403) {
                        alert('You must be logged in to add a booking.');
                        window.location.href = '/auth/login/'; 
                        return Promise.reject('Forbidden');
                    }
                    if (!response.ok) throw new Error('Booking request failed');
                    return response.json();
                })
                .then(data => {
                    showToast(data.message || 'Added to booking!', 'success');
                    closeModal();
                    setTimeout(() => { window.location.href = URLS.bookingRedirect; }, 1000); 
                })
                .catch(error => {
                     if (error !== 'Forbidden') {
                        console.error('Error adding to booking:', error);
                        showToast('Error: Could not add to booking.', 'error');
                    }
                });
            return; // Done handling click
        }

        // Handle Edit Button (fetches edit form)
        const editBtn = event.target.closest('#edit-venue-btn');
        if (editBtn) {
            const slug = editBtn.dataset.slug;
            if (!slug) return;
            const fetchUrl = URLS.getEditForm.replace('SLUG_PLACEHOLDER', slug);

            fetch(fetchUrl)
                .then(response => {
                    if (response.status === 403) {
                        showToast('You are not allowed to edit this venue.', 'error');
                        return Promise.reject('Forbidden'); 
                    }
                    if (!response.ok) throw new Error('Could not load edit form.');
                    return response.json();
                })
                .then(data => {
                    modalPanel.innerHTML = data.html; // Replace modal content
                })
                .catch(error => {
                    if (error !== 'Forbidden') {
                       console.error('Error fetching edit form:', error);
                       showToast(error.message || 'Error loading edit form.', 'error');
                    }
                });
            return; // Done handling click
       }

        // Handle Delete Button (shows confirmation/performs delete)
        const deleteBtn = event.target.closest('#delete-venue-btn');
        if (deleteBtn) {
             const slug = deleteBtn.dataset.slug;
             if (!slug) return;

             if (confirm(`Are you sure you want to delete this venue? This cannot be undone.`)) {
                const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value; // Get CSRF from form if possible
                 if (!csrfToken) {
                      // Fallback: try getting from main page meta or cookie if needed
                      showToast('CSRF token not found. Cannot delete.', 'error');
                      return;
                 }
                 const deleteUrl = `/ajax/delete-venue/${slug}/`; 

                 fetch(deleteUrl, {
                     method: 'POST',
                     headers: {
                         'X-CSRFToken': csrfToken,
                         'Content-Type': 'application/json' 
                     },
                     // body: JSON.stringify({}) // Add if needed by view
                 })
                 .then(response => {
                      if (response.status === 403) throw new Error('Forbidden: You cannot delete this venue.');
                      if (!response.ok) throw new Error('Delete request failed.');
                      return response.json();
                 })
                 .then(data => {
                     if (data.status === 'ok') {
                         closeModal();
                         showToast(data.message, 'success');
                         const cardToRemove = venueContainer.querySelector(`.venue-card[data-slug="${data.deleted_slug}"]`);
                         if (cardToRemove) cardToRemove.remove();
                     } else {
                         throw new Error(data.message || 'Could not delete venue.');
                     }
                 })
                 .catch(error => {
                     console.error('Error deleting venue:', error);
                     showToast(error.message, 'error');
                 });
             }
             return; // Done handling click
        }
    });

    // --- 6. MODAL FORM SUBMISSION HANDLER ---
    // Handles both Create and Edit form submissions
    modalPanel.addEventListener('submit', function(event) {
        if (event.target.id === 'venue-form') {
            event.preventDefault(); 
            const form = event.target;
            const formData = new FormData(form);
            const originalSlug = form.querySelector('#venue-slug-for-update')?.value;

            fetch(form.action, { // form.action set by backend (create or edit URL)
                method: 'POST',
                body: formData,
                headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // SUCCESS (Create or Edit)
                    closeModal();
                    showToast(data.message, 'success');
                    
                    if (originalSlug) { // It was an Edit
                        const originalCard = venueContainer.querySelector(`.venue-card[data-slug="${originalSlug}"]`);
                        if (originalCard && data.updated_card_html) {
                            originalCard.outerHTML = data.updated_card_html;
                        } else { // Fallback if card not found or HTML missing
                            console.warn('Could not find original card to update or missing HTML.');
                            // Optionally reload the whole list
                            form.dispatchEvent(new Event('submit', { cancelable: true })); // Trigger filter form submit
                        }
                    } else if (data.new_card_html) { // It was a Create
                        venueContainer.querySelector('.grid').insertAdjacentHTML('afterbegin', data.new_card_html);
                    }
                } else if (data.status === 'error' && data.form_html) {
                    // Validation error
                    modalPanel.innerHTML = data.form_html; // Re-render form with errors
                } else {
                    // Other server error
                    throw new Error(data.message || 'Form submission failed.');
                }
            })
            .catch(error => {
                console.error('Form submission error:', error);
                showToast(error.message || 'An error occurred.', 'error');
            });
        }
        // Note: Delete confirmation form submission would be handled here too if implemented
        // else if (event.target.id === 'delete-venue-form') { ... } 
    });
    
    // --- Close modal on overlay click ---
    modalOverlay.addEventListener('click', closeModal);
});