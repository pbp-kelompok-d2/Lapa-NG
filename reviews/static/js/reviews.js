// Configuration
const REVIEWS_JSON_URL = document.currentScript.getAttribute('data-json-url');
const ADD_REVIEW_AJAX_URL = document.currentScript.getAttribute('data-add-url');
const CSRF_TOKEN = document.currentScript.getAttribute('data-csrf-token');

// DOM Elements
let ratingStars, ratingInput, ratingText, reviewForm;

// Rating descriptions
const ratingDescriptions = {
    1: 'Sangat Buruk - 1 bintang',
    2: 'Buruk - 2 bintang', 
    3: 'Cukup - 3 bintang',
    4: 'Bagus - 4 bintang',
    5: 'Sangat Bagus - 5 bintang'
};

// Initialize rating stars interaction
function initializeRatingStars() {
    ratingStars = document.querySelectorAll('.rating-star');
    ratingInput = document.getElementById('rating');
    ratingText = document.getElementById('rating-text');

    ratingStars.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            ratingInput.value = rating;
            ratingText.textContent = ratingDescriptions[rating];
            
            // Update stars display
            ratingStars.forEach((s, index) => {
                const starSpan = s.querySelector('span');
                if (index < rating) {
                    starSpan.className = 'text-yellow-400';
                } else {
                    starSpan.className = 'text-gray-300';
                }
            });
        });
    });

    // Initialize with 5 stars
    if (ratingStars.length >= 5) {
        ratingStars[4].click();
    }
}

// Function to add review to DOM
function addReviewToDOM(review) {
    const reviewCards = document.getElementById('review-cards');
    const emptyState = document.getElementById('empty-reviews');
    
    // Hide empty state if shown
    emptyState.classList.add('hidden');
    
    // Create review card
    const reviewCard = document.createElement('div');
    reviewCard.className = 'bg-gray-50 rounded-lg p-6 border border-gray-200';
    reviewCard.innerHTML = `
        <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="font-semibold text-green-600">${review.user.charAt(0).toUpperCase()}</span>
                </div>
                <div>
                    <h3 class="font-semibold text-gray-900">${review.user}</h3>
                    <p class="text-sm text-gray-500">${review.created_at}</p>
                </div>
            </div>
            <div class="flex items-center space-x-1">
                ${'<span class="text-yellow-400 text-lg">★</span>'.repeat(review.rating)}
                ${'<span class="text-gray-300 text-lg">★</span>'.repeat(5 - review.rating)}
            </div>
        </div>
        
        <h4 class="font-bold text-lg text-gray-900 mb-2">${review.venue_name}</h4>
        <p class="text-gray-700 leading-relaxed">${review.comment}</p>
    `;
    
    // Add to the top
    if (reviewCards.firstChild) {
        reviewCards.insertBefore(reviewCard, reviewCards.firstChild);
    } else {
        reviewCards.appendChild(reviewCard);
    }
}

// Function to update review count
function updateReviewCount() {
    const reviewCount = document.querySelectorAll('#review-cards > div').length;
    const reviewCountElement = document.getElementById('review-count');
    if (reviewCountElement) {
        reviewCountElement.textContent = `${reviewCount} ulasan`;
    }
}

// Load reviews from server
async function loadReviews() {
    const loadingElement = document.getElementById('loading-reviews');
    const emptyState = document.getElementById('empty-reviews');
    const reviewCards = document.getElementById('review-cards');
    
    try {
        if (loadingElement) loadingElement.classList.remove('hidden');
        
        const response = await fetch(REVIEWS_JSON_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reviews = await response.json();
        
        // Hide loading
        if (loadingElement) loadingElement.classList.add('hidden');
        
        if (reviews.length === 0) {
            if (emptyState) emptyState.classList.remove('hidden');
        } else {
            // Clear existing reviews and add new ones
            if (reviewCards) {
                reviewCards.innerHTML = '';
                reviews.forEach(review => addReviewToDOM(review));
                updateReviewCount();
            }
        }
        
    } catch (error) {
        console.error('Error loading reviews:', error);
        if (loadingElement) loadingElement.classList.add('hidden');
        if (emptyState) {
            emptyState.classList.remove('hidden');
            emptyState.innerHTML = `
                <div class="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span class="text-3xl">⚠️</span>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">Gagal Memuat Ulasan</h3>
                <p class="text-gray-600 mb-6">Silakan refresh halaman atau coba lagi nanti.</p>
            `;
        }
    }
}

// Handle review form submission
async function handleReviewFormSubmit(e) {
    e.preventDefault();
    
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mx-auto"></div>';
    submitBtn.disabled = true;
    
    try {
        const formData = {
            venue_name: document.getElementById('venue_name').value,
            rating: parseInt(document.getElementById('rating').value),
            comment: document.getElementById('comment').value
        };
        
        const response = await fetch(ADD_REVIEW_AJAX_URL, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const newReview = await response.json();
            
            // Add new review to the top
            addReviewToDOM(newReview);
            
            // Reset form
            this.reset();
            // Reset to 5 stars
            if (ratingStars && ratingStars.length >= 5) {
                ratingStars[4].click();
            }
            
            // Show success message
            if (typeof showToast === 'function') {
                showToast('Sukses!', 'Ulasan berhasil ditambahkan', 'success');
            } else {
                alert('Ulasan berhasil ditambahkan!');
            }
            
            // Update review count
            updateReviewCount();
            
        } else {
            const errorData = await response.json();
            throw new Error(errorData.errors || 'Gagal menambahkan ulasan');
        }
        
    } catch (error) {
        console.error('Error:', error);
        if (typeof showToast === 'function') {
            showToast('Error', error.message, 'error');
        } else {
            alert('Error: ' + error.message);
        }
    } finally {
        // Reset button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Initialize the reviews page
function initializeReviewsPage() {
    // Initialize rating stars
    initializeRatingStars();
    
    // Load existing reviews
    loadReviews();
    
    // Add event listener to form
    reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', handleReviewFormSubmit);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeReviewsPage);