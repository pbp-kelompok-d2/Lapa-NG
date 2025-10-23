// reviews/static/js/reviews.js - KODE LENGKAP PENGGANTI

document.addEventListener("DOMContentLoaded", () => {
    // ===================================
    // KONFIGURASI DAN ELEMEN
    // ===================================
    const reviewCardsContainer = document.getElementById('review-cards-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const emptyState = document.getElementById('empty-state');
    const filterButtons = document.querySelectorAll('.filter-btn');

    let currentFilter = 'all'; // Menyimpan state filter saat ini
    let reviewIdToDelete = null; // Variabel untuk menyimpan ID yang akan dihapus

    // ===================================
    // FUNGSI UTAMA (MEMUAT REVIEW)
    // ===================================
    async function loadReviews(filter = 'all') {
        showLoading(true);
        try {
            const response = await fetch(`/reviews/get-reviews/?filter=${filter}`, { cache: 'no-store' });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const reviews = await response.json();
            reviewCardsContainer.innerHTML = ''; 
            if (reviews.length === 0) {
                showEmptyState(filter);
            } else {
                reviews.forEach(review => reviewCardsContainer.appendChild(createReviewCard(review)));
            }
        } catch (error) {
            showToast(`Gagal memuat ulasan: ${error.message}`, 'error');
        } finally {
            showLoading(false);
        }
    }

    // ===================================
    // FUNGSI PEMBUATAN KARTU REVIEW
    // ===================================
    function createReviewCard(review) {
        const card = document.createElement('div');
        card.className = 'review-card bg-white rounded-xl shadow-lg overflow-hidden flex flex-col transition-all duration-300 hover:shadow-2xl hover:-translate-y-1';
        card.dataset.reviewId = review.pk;
        const imageUrl = review.image_url || `https://placehold.co/400x300/e2e8f0/94a3b8?text=${encodeURIComponent(review.venue_name.charAt(0))}`;
        let starsHTML = Array(5).fill(0).map((_, i) => `<span class="text-xl ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}">★</span>`).join('');
        let buttonsHTML = '';
        if (review.can_modify) {
            buttonsHTML = `
                <div class="flex items-center space-x-2">
                    <button class="edit-btn p-2 rounded-full bg-gray-100 hover:bg-blue-100 text-blue-600 transition-colors" title="Edit Ulasan"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg></button>
                    <button class="delete-btn p-2 rounded-full bg-gray-100 hover:bg-red-100 text-red-600 transition-colors" title="Hapus Ulasan"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
                </div>`;
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
            </div>`;
        return card;
    }

    // ===================================
    // HANDLER UNTUK SEMUA AKSI (CREATE, UPDATE, DELETE)
    // ===================================

    // ADD REVIEW
    const addReviewForm = document.getElementById('add-review-form');
    if (addReviewForm) {
        addReviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('add-review-submit-btn');
            const formData = {
                venue_name: document.getElementById('venue_name_input').value.trim(),
                rating: parseInt(document.getElementById('rating_input').value),
                comment: document.getElementById('comment_input').value.trim(),
                image_url: document.getElementById('image_url_input').value.trim() || "",
            };
            setButtonLoading(submitBtn, true);
            try {
                const response = await fetch('/reviews/add-review/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify(formData),
                });
                const result = await response.json();
                if (!response.ok) {
                    const errorText = result.errors ? Object.values(result.errors).flat().join(' ') : result.message;
                    throw new Error(errorText || 'Terjadi kesalahan dari server.');
                }
                showToast('Ulasan berhasil ditambahkan!');
                closeModal(document.getElementById('add-review-modal'));
                addReviewForm.reset(); 
                setStars(document.getElementById('star-rating-input'), document.getElementById('rating_input'), 0);
                loadReviews(currentFilter); 
            } catch (error) {
                showToast(`Gagal: ${error.message}`, 'error');
            } finally {
                setButtonLoading(submitBtn, false, 'Kirim');
            }
        });
    }

    // EDIT REVIEW
    const editReviewForm = document.getElementById('edit-review-form');
    if(editReviewForm) {
        editReviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const reviewId = document.getElementById('edit_review_id_input').value;
            const submitBtn = document.getElementById('edit-review-submit-btn');
            const formData = {
                venue_name: document.getElementById('edit_venue_name_input').value.trim(),
                rating: parseInt(document.getElementById('edit_rating_input').value),
                comment: document.getElementById('edit_comment_input').value.trim(),
                image_url: document.getElementById('edit_image_url_input').value.trim() || "",
            };
            setButtonLoading(submitBtn, true);
            try {
                const response = await fetch(`/reviews/edit-review/${reviewId}/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
                    body: JSON.stringify(formData),
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.message || 'Gagal memperbarui.');
                showToast('Ulasan berhasil diperbarui!');
                closeModal(document.getElementById('edit-review-modal'));
                loadReviews(currentFilter);
            } catch (error) {
                showToast(`Error: ${error.message}`, 'error');
            } finally {
                setButtonLoading(submitBtn, false, 'Simpan Perubahan');
            }
        });
    }

    // --- PERUBAHAN UTAMA DIMULAI DI SINI ---

    // DELETE REVIEW: FUNGSI INI HANYA MEMBUKA MODAL KONFIRMASI
    function confirmDeleteReview(reviewId) {
        reviewIdToDelete = reviewId; // Simpan ID untuk digunakan nanti
        const confirmModal = document.getElementById('confirm-delete-modal');
        showModal(confirmModal);
    }

    // FUNGSI UNTUK EKSEKUSI PENGHAPUSAN SETELAH DIKONFIRMASI
    async function executeDelete() {
        if (!reviewIdToDelete) return;

        try {
            const response = await fetch(`/reviews/delete-review/${reviewIdToDelete}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);

            showToast('Ulasan berhasil dihapus.');
            loadReviews(currentFilter);
        } catch (error) {
            showToast(`Gagal menghapus: ${error.message}`, 'error');
        } finally {
            reviewIdToDelete = null; // Reset ID setelah selesai
            closeModal(document.getElementById('confirm-delete-modal'));
        }
    }

    // --- PERUBAHAN UTAMA SELESAI DI SINI ---

    // ===================================
    // EVENT LISTENERS (DELEGATION & MODALS)
    // ===================================
    reviewCardsContainer.addEventListener('click', (e) => {
        const reviewCard = e.target.closest('.review-card');
        if (!reviewCard) return;
        const reviewId = reviewCard.dataset.reviewId;

        if (e.target.closest('.view-detail-btn')) openDetailModal(reviewId);
        else if (e.target.closest('.edit-btn')) openEditModal(reviewId);
        // Panggil fungsi konfirmasi, bukan delete langsung
        else if (e.target.closest('.delete-btn')) confirmDeleteReview(reviewId);
    });

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            currentFilter = button.dataset.filter;
            filterButtons.forEach(btn => btn.classList.remove('active-filter'));
            button.classList.add('active-filter');
            loadReviews(currentFilter);
        });
    });

    initializeModals();

    // ===================================
    // FUNGSI UNTUK MODAL
    // ===================================
    function initializeModals() {
        // ADD MODAL
        const addModal = document.getElementById('add-review-modal');
        const openAddBtn = document.getElementById('open-add-review-modal');
        if (addModal && openAddBtn) {
            openAddBtn.addEventListener('click', () => showModal(addModal));
            document.getElementById('close-add-review-modal').addEventListener('click', () => closeModal(addModal));
            setupStarRating(document.getElementById('star-rating-input'), document.getElementById('rating_input'));
        }

        // EDIT MODAL
        const editModal = document.getElementById('edit-review-modal');
        if (editModal) {
            document.getElementById('close-edit-review-modal').addEventListener('click', () => closeModal(editModal));
            setupStarRating(document.getElementById('edit-star-rating-input'), document.getElementById('edit_rating_input'));
        }

        // DETAIL MODAL
        const detailModal = document.getElementById('review-detail-modal');
        if(detailModal) {
            document.getElementById('close-detail-modal').addEventListener('click', () => closeModal(detailModal));
        }
        
        // CONFIRM DELETE MODAL (BARU)
        const confirmModal = document.getElementById('confirm-delete-modal');
        if(confirmModal) {
            document.getElementById('cancel-delete-btn').addEventListener('click', () => closeModal(confirmModal));
            document.getElementById('confirm-delete-btn').addEventListener('click', executeDelete);
        }
    }

    async function openDetailModal(reviewId) {
        const modal = document.getElementById('review-detail-modal');
        const loading = document.getElementById('detail-modal-loading');
        const body = document.getElementById('detail-modal-body');
        showModal(modal);
        loading.classList.remove('hidden');
        body.classList.add('hidden');
        try {
            const response = await fetch(`/reviews/get-review-detail/${reviewId}/`);
            const result = await response.json();
            if (result.status !== 'success') throw new Error(result.message);
            const review = result.data;
            document.getElementById('detail-venue-name').textContent = review.venue_name;
            document.getElementById('detail-comment').textContent = review.comment;
            document.getElementById('detail-user').textContent = review.user_username;
            document.getElementById('detail-date').textContent = review.created_at.split(',')[0];
            document.getElementById('detail-image').src = review.image_url || `https://placehold.co/600x400/e2e8f0/94a3b8?text=Tidak+Ada+Foto`;
            const ratingContainer = document.getElementById('detail-rating');
            ratingContainer.innerHTML = Array(5).fill(0).map((_, i) => `<span class="text-2xl ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}">★</span>`).join('');
            loading.classList.add('hidden');
            body.classList.remove('hidden');
        } catch (error) {
            loading.innerHTML = `<p class="text-red-500 text-center">Gagal memuat detail ulasan.</p>`;
        }
    }

    async function openEditModal(reviewId) {
        const modal = document.getElementById('edit-review-modal');
        showModal(modal);
        try {
            const response = await fetch(`/reviews/get-review-detail/${reviewId}/`);
            const result = await response.json();
            if (result.status !== 'success') throw new Error(result.message);
            const review = result.data;
            document.getElementById('edit_review_id_input').value = review.pk;
            document.getElementById('edit_venue_name_input').value = review.venue_name;
            document.getElementById('edit_comment_input').value = review.comment;
            document.getElementById('edit_image_url_input').value = review.image_url || '';
            setStars(document.getElementById('edit-star-rating-input'), document.getElementById('edit_rating_input'), review.rating);
        } catch (error) {
            showToast('Gagal mengambil data untuk diedit.', 'error');
            closeModal(modal);
        }
    }

    // ===================================
    // FUNGSI HELPERS
    // ===================================
    function getCsrfToken() { return document.querySelector('[name=csrfmiddlewaretoken]').value; }
    function showLoading(isLoading) {
        loadingSpinner.classList.toggle('hidden', !isLoading);
        reviewCardsContainer.classList.toggle('hidden', isLoading);
        if (isLoading) emptyState.classList.add('hidden');
    }
    function showEmptyState(filter) {
        emptyState.classList.remove('hidden');
        const title = emptyState.querySelector('h2');
        const text = emptyState.querySelector('p');
        if (filter === 'my_reviews') {
            title.textContent = "Anda Belum Punya Review";
            text.textContent = "Tambahkan review pertama Anda untuk lapangan yang pernah Anda kunjungi!";
        } else {
            title.textContent = "Belum Ada Ulasan";
            text.textContent = "Jadilah yang pertama memberikan ulasan untuk lapangan di LapaNG!";
        }
    }
    function showModal(modal) {
        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.remove('opacity-0'), 10);
        setTimeout(() => modal.querySelector('.modal-content').classList.remove('opacity-0', 'scale-95'), 50);
    }
    function closeModal(modal) {
        modal.querySelector('.modal-content').classList.add('opacity-0', 'scale-95');
        modal.classList.add('opacity-0');
        setTimeout(() => modal.classList.add('hidden'), 300);
    }
    function setButtonLoading(btn, isLoading, defaultText = 'Kirim') {
        btn.disabled = isLoading;
        btn.innerHTML = isLoading ? '<div class="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mx-auto"></div>' : defaultText;
    }
    function setupStarRating(container, input) {
        container.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', (e) => {
                e.stopPropagation();
                setStars(container, input, star.dataset.value);
            });
        });
    }
    function setStars(container, input, value) {
        const ratingDescriptions = { 1: 'Sangat Buruk', 2: 'Buruk', 3: 'Cukup', 4: 'Bagus', 5: 'Sangat Bagus' };
        const ratingTextEl = container.nextElementSibling;
        input.value = value;
        if(ratingTextEl) ratingTextEl.textContent = `${ratingDescriptions[value] || ''} (${value} bintang)`;
        container.querySelectorAll('.star').forEach(s => {
            s.classList.toggle('text-yellow-400', s.dataset.value <= value);
            s.classList.toggle('text-gray-300', s.dataset.value > value);
        });
    }
    function showToast(message, type = 'success') {
        const toastContainer = document.body;
        const toast = document.createElement('div');
        const bgColor = type === 'error' ? 'bg-red-500' : 'bg-green-500';
        toast.className = `fixed bottom-5 right-5 ${bgColor} text-white py-3 px-6 rounded-lg shadow-xl transform translate-y-full opacity-0 transition-all duration-500 ease-out`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => { toast.classList.remove('translate-y-full', 'opacity-0'); }, 100);
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }
    
    // ===================================
    // INISIALISASI
    // ===================================
    loadReviews();
});