document.addEventListener("DOMContentLoaded", () => {
    // Cek jika user-data ada sebelum parsing
    let userData = null;
    const userDataElement = document.getElementById('user-data');
    if (userDataElement) {
        try { userData = JSON.parse(userDataElement.textContent); } 
        catch (e) { console.error("Gagal parse user-data JSON:", e); }
    }

    // Elemen & URL
    const reviewCardsContainer = document.getElementById('review-cards-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const emptyState = document.getElementById('empty-state');
    const GET_REVIEWS_URL = '/reviews/get-reviews/';
    const ADD_REVIEW_URL = '/reviews/add-review/';
    const EDIT_REVIEW_URL_PREFIX = '/reviews/edit-review/';
    const DELETE_REVIEW_URL_PREFIX = '/reviews/delete-review/';
    const GET_REVIEW_DETAIL_URL_PREFIX = '/reviews/get-review-detail/';

    // ===================================
    // FUNGSI UTAMA (Memuat Semua Review)
    // ===================================
    async function loadReviews() {
        showLoading(true);
        try {
            const response = await fetch(GET_REVIEWS_URL, { cache: 'no-store' }); // Mencegah caching
            if (!response.ok) throw new Error('Gagal mengambil data dari server.');
            const reviews = await response.json();
            reviewCardsContainer.innerHTML = '';

            if (reviews.length === 0) {
                showEmptyState();
            } else {
                reviews.forEach(review => {
                    reviewCardsContainer.appendChild(createReviewCard(review));
                });
            }
        } catch (error) {
            showErrorAlert('Gagal memuat ulasan.', error.toString());
        } finally {
            showLoading(false);
        }
    }

    function createReviewCard(review) {
        // ... (Kode ini tidak perlu diubah, biarkan seperti sebelumnya)
        const card = document.createElement('div');
        card.className = 'review-card bg-white rounded-xl shadow-lg overflow-hidden flex flex-col transition-all duration-300 hover:shadow-2xl hover:-translate-y-1';
        card.dataset.reviewId = review.pk;
        const imageUrl = review.image_url || `https://placehold.co/400x300/e2e8f0/94a3b8?text=${review.venue_name.charAt(0)}`;
        let starsHTML = Array(5).fill(0).map((_, i) => `<span class="text-xl ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}">★</span>`).join('');
        let buttonsHTML = '';
        if (review.can_modify) {
            buttonsHTML = `
                <div class="flex items-center space-x-2">
                    <button class="edit-btn p-2 rounded-full bg-gray-100 hover:bg-blue-100 text-blue-600 transition-colors" title="Edit Ulasan"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg></button>
                    <button class="delete-btn p-2 rounded-full bg-gray-100 hover:bg-red-100 text-red-600 transition-colors" title="Hapus Ulasan"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
                </div>
            `;
        }
        card.innerHTML = `
            <div class="h-48 bg-gray-100"><img src="${imageUrl}" alt="Foto ${review.venue_name}" class="w-full h-full object-cover" onerror="this.src='https://placehold.co/400x300/e2e8f0/94a3b8?text=Error';"></div>
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="font-bold font-heading text-lg text-gray-800 truncate mb-1" title="${review.venue_name}">${review.venue_name}</h3>
                <p class="text-xs text-gray-500 mb-2">Oleh: <strong class="text-gray-700">${review.user_username}</strong></p>
                <div class="flex items-center justify-between mb-3"><div class="flex items-center space-x-1">${starsHTML}</div><span class="font-semibold text-gray-700 text-sm">${review.rating}/5</span></div>
                <div class="mt-auto flex justify-between items-center pt-2">
                    <button class="view-detail-btn w-auto bg-orange-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-orange-600 transition-colors text-sm">Lihat Komentar</button>
                    ${buttonsHTML}
                </div>
            </div>
        `;
        return card;
    }

    // ===================================
    // CRUD: CREATE (TAMBAH REVIEW)
    // ===================================
    const addReviewForm = document.getElementById('add-review-form');
    if (addReviewForm) {
        addReviewForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Ini adalah baris terpenting untuk mencegah reload
            const submitBtn = document.getElementById('add-review-submit-btn');
            
            const formData = {
                venue_name: document.getElementById('venue_name_input').value,
                rating: parseInt(document.getElementById('rating_input').value),
                comment: document.getElementById('comment_input').value,
                image_url: document.getElementById('image_url_input').value || "",
            };

            setButtonLoading(submitBtn, true);

            try {
                const response = await fetch(ADD_REVIEW_URL, {
                    method: 'POST', // Mengirim sebagai POST
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify(formData),
                });
                const result = await response.json();

                if (!response.ok) {
                    const errorText = result.errors ? JSON.stringify(result.errors) : result.message;
                    throw new Error(errorText || 'Terjadi kesalahan dari server.');
                }
                
                showSuccessAlert('Ulasan berhasil ditambahkan!');
                closeModal(document.getElementById('add-review-modal'));
                loadReviews(); // Memuat ulang kartu setelah sukses

            } catch (error) {
                showErrorAlert('Gagal Menambahkan Ulasan', error.message);
            } finally {
                setButtonLoading(submitBtn, false, 'Kirim');
            }
        });
    }

    // ===================================
    // EVENT DELEGATION DAN FUNGSI LAINNYA
    // ===================================
    reviewCardsContainer.addEventListener('click', (e) => {
        const reviewCard = e.target.closest('.review-card');
        if (!reviewCard) return;
        const reviewId = reviewCard.dataset.reviewId;

        if (e.target.closest('.view-detail-btn')) openDetailModal(reviewId);
        else if (e.target.closest('.edit-btn')) openEditModal(reviewId);
        else if (e.target.closest('.delete-btn')) deleteReview(reviewId);
    });

    // ===================================
    // CRUD: READ (DETAIL)
    // ===================================
    async function openDetailModal(reviewId) {
        const modal = document.getElementById('review-detail-modal');
        const content = document.getElementById('review-detail-modal-content');
        const loading = document.getElementById('detail-modal-loading');
        const body = document.getElementById('detail-modal-body');

        showModal(modal, content);
        loading.classList.remove('hidden');
        body.classList.add('hidden');

        try {
            const response = await fetch(`${GET_REVIEW_DETAIL_URL_PREFIX}${reviewId}/`);
            const result = await response.json();
            if (!result.status === 'success') throw new Error(result.message);

            const review = result.data;
            document.getElementById('detail-venue-name').textContent = review.venue_name;
            document.getElementById('detail-comment').textContent = review.comment;
            document.getElementById('detail-user').textContent = review.user_username;
            document.getElementById('detail-date').textContent = review.created_at.split(',')[0];
            document.getElementById('detail-image').src = review.image_url || `https://placehold.co/600x400/e2e8f0/94a3b8?text=Tidak+Ada+Foto`;

            const ratingContainer = document.getElementById('detail-rating');
            ratingContainer.innerHTML = Array(5).fill(0).map((_, i) =>
                `<span class="text-2xl ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}">★</span>`
            ).join('');

            loading.classList.add('hidden');
            body.classList.remove('hidden');
        } catch (error) {
            loading.innerHTML = `<p class="text-red-500">Gagal memuat detail ulasan.</p>`;
        }
    }

    // ===================================
    // CRUD: UPDATE (EDIT)
    // ===================================
    async function openEditModal(reviewId) {
        const modal = document.getElementById('edit-review-modal');
        const content = document.getElementById('edit-review-modal-content');
        showModal(modal, content);

        try {
            // Ambil data terbaru untuk di-edit
            const response = await fetch(`${GET_REVIEW_DETAIL_URL_PREFIX}${reviewId}/`);
            const result = await response.json();
            if (result.status !== 'success') throw new Error(result.message);
            
            const review = result.data;
            document.getElementById('edit_review_id_input').value = review.pk;
            document.getElementById('edit_venue_name_input').value = review.venue_name;
            document.getElementById('edit_comment_input').value = review.comment;
            document.getElementById('edit_image_url_input').value = review.image_url || '';
            
            // Set rating di modal edit
            const ratingInput = document.getElementById('edit_rating_input');
            const starsContainer = document.getElementById('edit-star-rating-input');
            setStars(starsContainer, ratingInput, review.rating);

        } catch (error) {
            alert('Gagal mengambil data untuk diedit.');
            closeModal(modal, content);
        }
    }
    
    document.getElementById('edit-review-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const reviewId = document.getElementById('edit_review_id_input').value;
        const submitBtn = document.getElementById('edit-review-submit-btn');

        const formData = {
            venue_name: document.getElementById('edit_venue_name_input').value,
            rating: parseInt(document.getElementById('edit_rating_input').value),
            comment: document.getElementById('edit_comment_input').value,
            image_url: document.getElementById('edit_image_url_input').value || "",
        };

        setButtonLoading(submitBtn, true);

        try {
            const response = await fetch(`${EDIT_REVIEW_URL_PREFIX}${reviewId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify(formData),
            });
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                alert('Ulasan berhasil diperbarui!');
                const modal = document.getElementById('edit-review-modal');
                const content = document.getElementById('edit-review-modal-content');
                closeModal(modal, content);
                loadReviews();
            } else {
                alert(`Error: ${result.message || JSON.stringify(result.errors)}`);
            }
        } catch (error) {
            alert('Terjadi kesalahan saat menyimpan perubahan.');
        } finally {
            setButtonLoading(submitBtn, false, 'Simpan Perubahan');
        }
    });

    // ===================================
    // CRUD: DELETE
    // ===================================
    async function deleteReview(reviewId) {
        if (!confirm('Apakah Anda yakin ingin menghapus ulasan ini?')) {
            return;
        }

        try {
            const response = await fetch(`${DELETE_REVIEW_URL_PREFIX}${reviewId}/`, {
                method: 'POST', // Menggunakan POST sesuai setup di view
                headers: { 'X-CSRFToken': getCsrfToken() },
            });
            const result = await response.json();

            if (response.ok && result.status === 'success') {
                alert('Ulasan berhasil dihapus.');
                loadReviews();
            } else {
                alert(`Gagal menghapus ulasan: ${result.message}`);
            }
        } catch (error) {
            alert('Terjadi kesalahan jaringan.');
        }
    }
    
    // ===================================
    // FUNGSI BANTUAN (Helpers)
    // ===================================
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function showLoading(isLoading) {
        loadingSpinner.classList.toggle('hidden', !isLoading);
        if (isLoading) {
            reviewCardsContainer.innerHTML = '';
            emptyState.classList.add('hidden');
        }
    }

    function showEmptyState() {
        emptyState.classList.remove('hidden');
    }

    function showModal(modal, content) {
        modal.classList.remove('hidden', 'flex');
        modal.classList.add('flex');
        setTimeout(() => content.classList.remove('opacity-0', 'scale-95'), 10);
    }
    
    function closeModal(modal, content) {
        content.classList.add('opacity-0', 'scale-95');
        setTimeout(() => modal.classList.add('hidden'), 300);
    }

    function setButtonLoading(btn, isLoading, defaultText = 'Kirim') {
        btn.disabled = isLoading;
        if (isLoading) {
            btn.innerHTML = '<div class="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mx-auto"></div>';
        } else {
            btn.innerHTML = defaultText;
        }
    }

    // Fungsi untuk setup bintang rating
    function setupStarRating(container, input) {
        const ratingDescriptions = { 1: 'Sangat Buruk', 2: 'Buruk', 3: 'Cukup', 4: 'Bagus', 5: 'Sangat Bagus' };
        const ratingText = container.nextElementSibling;

        container.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', () => {
                const value = star.dataset.value;
                setStars(container, input, value, ratingDescriptions);
            });
        });
    }
    
    function setStars(container, input, value) {
        const ratingDescriptions = { 1: 'Sangat Buruk', 2: 'Buruk', 3: 'Cukup', 4: 'Bagus', 5: 'Sangat Bagus' };
        const ratingText = container.nextElementSibling;
        
        input.value = value;
        if(ratingText) ratingText.textContent = `${ratingDescriptions[value]} (${value} bintang)`;
        
        container.querySelectorAll('.star').forEach(s => {
            s.classList.toggle('text-yellow-400', s.dataset.value <= value);
            s.classList.toggle('text-gray-300', s.dataset.value > value);
        });
    }

    // Inisialisasi modal tambah & edit
    const addReviewModal = document.getElementById('add-review-modal');
    document.getElementById('open-add-review-modal').addEventListener('click', () => showModal(addReviewModal, document.getElementById('add-review-modal-content')));
    document.getElementById('close-add-review-modal').addEventListener('click', () => closeModal(addReviewModal, document.getElementById('add-review-modal-content')));
    setupStarRating(document.getElementById('star-rating-input'), document.getElementById('rating_input'));
    
    const editReviewModal = document.getElementById('edit-review-modal');
    document.getElementById('close-edit-review-modal').addEventListener('click', () => closeModal(editReviewModal, document.getElementById('edit-review-modal-content')));
    setupStarRating(document.getElementById('edit-star-rating-input'), document.getElementById('edit_rating_input'));
    
    const detailModal = document.getElementById('review-detail-modal');
    document.getElementById('close-detail-modal').addEventListener('click', () => closeModal(detailModal, document.getElementById('review-detail-modal-content')));


    // Mulai aplikasi
    loadReviews();
});