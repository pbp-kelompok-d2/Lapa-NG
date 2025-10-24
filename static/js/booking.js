// ===============================
// ========== TOAST ==============
// ===============================
/**
 * Displays a toast notification.
 * @param {string} message The message to display.
 * @param {string} type 'success', 'error', or 'info'
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `p-4 rounded-lg shadow-lg text-white font-medium transition-all duration-300 transform translate-x-full`;
    toast.innerText = message;

    if (type === 'success') {
        toast.classList.add('bg-green-600');
    } else if (type === 'error') {
        toast.classList.add('bg-red-600');
    } else {
        toast.classList.add('bg-blue-600');
    }

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);

    // Animate out
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-full');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 3000);
}

// ===============================
// ======= CSRF HELPER ===========
// ===============================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===============================
// ======= EDIT BOOKING ==========
// ===============================
document.addEventListener('DOMContentLoaded', () => {
    const modal = new bootstrap.Modal(document.getElementById('editBookingModal'));
    const modalBody = document.getElementById('modalFormContainer');

    // Saat tombol edit diklik
    document.querySelectorAll('.edit-booking').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            fetch(`/booking/edit/${id}/`)
                .then(res => res.json())
                .then(data => {
                    modalBody.innerHTML = data.html_form;
                    modal.show();

                    const form = document.getElementById('editBookingForm');
                    form.addEventListener('submit', e => {
                        e.preventDefault();
                        const formData = new FormData(form);
                        fetch(`/booking/edit/${id}/`, {
                            method: 'POST',
                            body: formData,
                            headers: { 'X-Requested-With': 'XMLHttpRequest' }
                        })
                            .then(res => res.json())
                            .then(data => {
                                if (data.success) {
                                    modal.hide();
                                    // Update tampilan waktu
                                    document.getElementById(`time-${id}`).textContent =
                                        `${formData.get('start_time')} - ${formData.get('end_time')}`;
                                    showToast('Booking berhasil diperbarui!', 'success');
                                } else {
                                    showToast('Gagal menyimpan perubahan.', 'error');
                                }
                            })
                            .catch(() => showToast('Terjadi kesalahan server.', 'error'));
                    });
                });
        });
    });
});

// ===============================
// ======= DELETE BOOKING ========
// ===============================
document.querySelectorAll('a[href*="remove_from_cart"]').forEach(link => {
    link.addEventListener('click', async (e) => {
        e.preventDefault();
        const url = link.getAttribute('href');
        const modal = link.closest('dialog');
        if (modal) modal.close();

        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });
            const data = await response.json();

            if (data.success) {
                showToast('Venue berhasil dihapus dari keranjang.', 'error');
                setTimeout(() => {
                    if (data.empty) {
                        window.location.href = '/booking/empty/';
                    } else {
                        window.location.reload();
                    }
                }, 800);
            } else {
                showToast('Gagal menghapus venue.', 'error');
            }
        } catch {
            showToast('Gagal terhubung ke server.', 'error');
        }
    });
});
