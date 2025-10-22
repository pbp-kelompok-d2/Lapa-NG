document.addEventListener("DOMContentLoaded", () => {
    
    // URLs (diasumsikan dari template, tapi kita hardcode path-nya)
    const GET_REVIEWS_URL = '/reviews/get-reviews/';
    const ADD_REVIEW_URL = '/reviews/add-review/';
    const GET_REVIEW_DETAIL_URL = '/reviews/get-review-detail/'; // prefix
    const CSRF_TOKEN = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Elemen Utama
    const reviewCardsContainer = document.getElementById('review-cards-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const emptyState = document.getElementById('empty-state');

    // Elemen Modal "Add Review"
    const addReviewModal = document.getElementById('add-review-modal');
    const addReviewModalContent = document.getElementById('add-review-modal-content');
    const openAddReviewModalBtn = document.getElementById('open-add-review-modal');
    const closeAddReviewModalBtn = document.getElementById('close-add-review-modal');
    const addReviewForm = document.getElementById('add-review-form');
    const addReviewSubmitBtn = document.getElementById('add-review-submit-btn');

    // Elemen Modal "Detail Review"
    const detailModal = document.getElementById('review-detail-modal');
    const detailModalContent = document.getElementById('review-detail-modal-content');
    const closeDetailModalBtn = document.getElementById('close-detail-modal');
    const detailModalLoading = document.getElementById('detail-modal-loading');
    const detailModalBody = document.getElementById('detail-modal-body');

    // Elemen Bintang Rating
    const starRatingInput = document.getElementById('star-rating-input');
    const stars = starRatingInput.querySelectorAll('.star');
    const ratingHiddenInput = document.getElementById('rating_input');
    const ratingText = document.getElementById('rating-text');
    
    const ratingDescriptions = {
        1: 'Sangat Buruk',
        2: 'Buruk',
        3: 'Cukup',
        4: 'Bagus',
        5: 'Sangat Bagus'
    };

    // ===================================
    // FUNGSI UTAMA (Memuat Review)
    // ===================================
    async function loadReviews() {
        showLoading();
        try {
            const response = await fetch(GET_REVIEWS_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const reviews = await response.json();

            reviewCardsContainer.innerHTML = ''; // Kosongkan kontainer

            if (reviews.length === 0) {
                showEmptyState();
            } else {
                reviews.forEach(review => {
                    const reviewCard = createReviewCard(review);
                    reviewCardsContainer.appendChild(reviewCard);
                });
                hideLoading();
            }
        } catch (error) {
            console.error('Error loading reviews:', error);
            reviewCardsContainer.innerHTML = `<p class="text-center text-red-400 col-span-full">Gagal memuat ulasan. Silakan coba lagi nanti.</p>`;
            hideLoading();
        }
    }

    function createReviewCard(review) {
        const card = document.createElement('div');
        card.className = 'bg-white rounded-xl shadow-lg overflow-hidden transform transition-all duration-300 hover:shadow-xl hover:-translate-y-1';
        
        // Tentukan URL gambar. Jika kosong, gunakan placeholder
        const imageUrl = review.image_url ? review.image_url : `https://placehold.co/400x300/e2e8f0/94a3b8?text=${review.venue_name.charAt(0)}`;
        
        // Buat bintang
        let starsHTML = '';
        for (let i = 1; i <= 5; i++) {
            starsHTML += `<span class="text-lg ${i <= review.rating ? 'text-yellow-400' : 'text-gray-300'}">★</span>`;
        }

        card.innerHTML = `
            <div class="h-48 bg-gray-100">
                <img src="${imageUrl}" alt="Foto ${review.venue_name}" class="w-full h-full object-cover" onerror="this.src='https://placehold.co/400x300/e2e8f0/94a3b8?text=Error'; this.onerror=null;">
            </div>
            <div class="p-5">
                <h3 class="font-bold font-heading text-xl text-gray-800 truncate mb-2" title="${review.venue_name}">${review.venue_name}</h3>
                <p class="text-sm text-gray-500 mb-3">
                    Diulas oleh: <strong class="text-gray-700">${review.user_username}</strong>
                </p>
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-1">
                        ${starsHTML}
                    </div>
                    <span class="font-bold text-gray-700">${review.rating}/5</span>
                </div>
                <button class="view-detail-btn w-full bg-orange-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-orange-600 transition-colors duration-300" data-review-id="${review.pk}">
                    Lihat Komentar
                </button>
            </div>
        `;

        // Tambahkan event listener ke tombol "Lihat Komentar"
        card.querySelector('.view-detail-btn').addEventListener('click', () => {
            openDetailModal(review.pk);
        });

        return card;
    }

    // ===================================
    // FUNGSI BANTUAN (Loading & Empty State)
    // ===================================
    function showLoading() {
        loadingSpinner.classList.remove('hidden');
        emptyState.classList.add('hidden');
        reviewCardsContainer.innerHTML = '';
    }

    function hideLoading() {
        loadingSpinner.classList.add('hidden');
    }

    function showEmptyState() {
        loadingSpinner.classList.add('hidden');
        emptyState.classList.remove('hidden');
        reviewCardsContainer.innerHTML = '';
    }

    // ===================================
    // LOGIKA MODAL "ADD REVIEW"
    // ===================================

    // Buka Modal
    openAddReviewModalBtn.addEventListener('click', () => {
        addReviewForm.reset(); // Reset form setiap dibuka
        resetStars(); // Reset bintang
        addReviewModal.classList.remove('hidden');
        addReviewModal.classList.add('flex');
        setTimeout(() => {
            addReviewModalContent.classList.remove('opacity-0', 'scale-95');
        }, 10);
    });

    // Tutup Modal
    function closeAddReviewModal() {
        addReviewModalContent.classList.add('opacity-0', 'scale-95');
        setTimeout(() => {
            addReviewModal.classList.add('hidden');
            addReviewModal.classList.remove('flex');
        }, 300); // Sesuaikan dengan durasi transisi
    }
    closeAddReviewModalBtn.addEventListener('click', closeAddReviewModal);
    
    // Logika Bintang Rating
    function resetStars() {
        stars.forEach(s => s.classList.remove('selected', 'text-yellow-400'));
        stars.forEach(s => s.classList.add('text-gray-300'));
        ratingHiddenInput.value = '';
        ratingText.textContent = 'Pilih rating...';
    }

    stars.forEach(star => {
        star.addEventListener('click', () => {
            const value = star.dataset.value;
            ratingHiddenInput.value = value;
            ratingText.textContent = `${ratingDescriptions[value]} (${value} bintang)`;
            
            stars.forEach(s => {
                s.classList.remove('selected', 'text-yellow-400');
                s.classList.add('text-gray-300');
                if (s.dataset.value <= value) {
                    s.classList.add('selected', 'text-yellow-400');
                    s.classList.remove('text-gray-300');
                }
            });
        });

        // Efek hover
        star.addEventListener('mouseover', () => {
            stars.forEach(s => {
                s.classList.remove('text-yellow-400');
                s.classList.add('text-gray-300');
                if (s.dataset.value <= star.dataset.value) {
                    s.classList.add('text-yellow-400');
                    s.classList.remove('text-gray-300');
                }
            });
        });
    });

    starRatingInput.addEventListener('mouseout', () => {
        const selectedValue = ratingHiddenInput.value;
        stars.forEach(s => {
            s.classList.remove('text-yellow-400');
            s.classList.add('text-gray-300');
            if (selectedValue && s.dataset.value <= selectedValue) {
                s.classList.add('text-yellow-400');
                s.classList.remove('text-gray-300');
            }
        });
    });

    resetStars(); // Inisialisasi bintang saat load

    // Submit Form "Add Review"
    addReviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            venue_name: document.getElementById('venue_name_input').value,
            rating: parseInt(ratingHiddenInput.value),
            comment: document.getElementById('comment_input').value,
            image_url: document.getElementById('image_url_input').value || null, // Kirim null jika kosong
        };

        // Validasi sederhana
        if (!formData.venue_name || !formData.rating || !formData.comment) {
            showToast('Error', 'Nama lapangan, rating, dan komentar wajib diisi.', 'error');
            return;
        }

        // Tampilkan loading di tombol
        addReviewSubmitBtn.disabled = true;
        addReviewSubmitBtn.innerHTML = '<div class="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mx-auto"></div>';

        try {
            const response = await fetch(ADD_REVIEW_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN,
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                showToast('Sukses!', 'Ulasan berhasil ditambahkan.', 'success');
                closeAddReviewModal();
                loadReviews(); // Muat ulang semua review
            } else {
                // Tangani error dari server (misal validasi)
                let errorMessage = result.message || 'Gagal menambahkan ulasan.';
                if (result.errors) {
                    errorMessage = Object.values(result.errors).flat().join(' ');
                }
                showToast('Error', errorMessage, 'error');
            }
        } catch (error) {
            console.error('Error submitting review:', error);
            showToast('Error', 'Terjadi kesalahan. Coba lagi nanti.', 'error');
        } finally {
            // Kembalikan tombol ke state normal
            addReviewSubmitBtn.disabled = false;
            addReviewSubmitBtn.innerHTML = 'Kirim';
        }
    });


    // ===================================
    // LOGIKA MODAL "DETAIL REVIEW"
    // ===================================
    async function openDetailModal(reviewId) {
        // Tampilkan modal dan loading state
        detailModal.classList.remove('hidden');
        detailModal.classList.add('flex');
        detailModalLoading.classList.remove('hidden');
        detailModalBody.classList.add('hidden');
        
        setTimeout(() => {
            detailModalContent.classList.remove('opacity-0', 'scale-95');
        }, 10);

        try {
            const response = await fetch(`${GET_REVIEW_DETAIL_URL}${reviewId}/`);
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                const review = result.data;
                
                // Isi data ke modal
                document.getElementById('detail-venue-name').textContent = review.venue_name;
                document.getElementById('detail-comment').textContent = review.comment;
                document.getElementById('detail-user').textContent = review.user_username;
                document.getElementById('detail-date').textContent = review.created_at.split(',')[0]; // Ambil tanggal saja

                // Set gambar
                const img = document.getElementById('detail-image');
                if (review.image_url) {
                    img.src = review.image_url;
                    img.alt = `Foto ulasan ${review.venue_name}`;
                } else {
                    // Placeholder jika tidak ada gambar
                    img.src = `https://placehold.co/600x400/e2e8f0/94a3b8?text=Tidak+Ada+Foto`;
                    img.alt = `Tidak ada foto ulasan`;
                }
                
                // Buat bintang
                const detailRatingContainer = document.getElementById('detail-rating');
                detailRatingContainer.innerHTML = '';
                for (let i = 1; i <= 5; i++) {
                    const starSpan = document.createElement('span');
                    starSpan.textContent = '★';
                    starSpan.className = i <= review.rating ? 'text-yellow-400' : 'text-gray-300';
                    detailRatingContainer.appendChild(starSpan);
                }

                // Tampilkan konten, sembunyikan loading
                detailModalLoading.classList.add('hidden');
                detailModalBody.classList.remove('hidden');

            } else {
                throw new Error(result.message || 'Gagal mengambil data');
            }
        } catch (error) {
            console.error('Error fetching review detail:', error);
            detailModalLoading.innerHTML = `<p class="text-red-500">Gagal memuat detail ulasan.</p>`;
        }
    }

    // Tutup Modal Detail
    function closeDetailModal() {
        detailModalContent.classList.add('opacity-0', 'scale-95');
        setTimeout(() => {
            detailModal.classList.add('hidden');
            detailModal.classList.remove('flex');
            
            // Reset state modal detail untuk pemanggilan berikutnya
            detailModalLoading.classList.remove('hidden');
            detailModalBody.classList.add('hidden');
            detailModalLoading.innerHTML = '<div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-green-500 mx-auto"></div><p class="text-gray-600 mt-4">Memuat detail...</p>';
        }, 300);
    }
    closeDetailModalBtn.addEventListener('click', closeDetailModal);

    // ===================================
    // FUNGSI TOAST NOTIFICATION
    // ===================================
    function showToast(title, message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast w-80 max-w-sm bg-white rounded-lg shadow-lg p-4 border-l-4 ${type === 'success' ? 'border-green-500' : 'border-red-500'}`;
        
        toast.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="w-6 h-6 ${type === 'success' ? 'text-green-500' : 'text-red-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        ${type === 'success' ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>' : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>'}
                    </svg>
                </div>
                <div class="ml-3 w-0 flex-1">
                    <p class="text-sm font-bold text-gray-900">${title}</p>
                    <p class="mt-1 text-sm text-gray-600">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                    <button class="toast-close-btn inline-flex text-gray-400 hover:text-gray-500">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                    </button>
                </div>
            </div>
        `;

        toast.querySelector('.toast-close-btn').addEventListener('click', () => {
            toast.classList.add('toast-exit');
            setTimeout(() => toast.remove(), 500);
        });

        toastContainer.appendChild(toast);

        // Hapus toast setelah 5 detik
        setTimeout(() => {
            toast.classList.add('toast-exit');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 500);
        }, 5000);
    }

    // ===================================
    // INISIALISASI
    // ===================================
    loadReviews();
});
