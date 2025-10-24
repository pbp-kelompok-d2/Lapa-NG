(function () {
  // Utilities
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const CSRF_TOKEN = getCookie('csrftoken');

  function safeParseInt(v, def = 0) {
    const n = parseInt(v, 10);
    return Number.isFinite(n) ? n : def;
  }

  // Toast
  function showToast(message = 'Saved', { duration = 2500 } = {}) {
    const toastWrap = document.getElementById('global-toast');
    const toastInner = document.getElementById('global-toast-inner');
    const toastMsg = document.getElementById('global-toast-message');
    if (!toastWrap || !toastInner || !toastMsg) return;

    toastMsg.textContent = message;
    toastWrap.classList.remove('hidden');
    toastInner.classList.remove('toast-hide');
    toastInner.classList.add('toast-show');

    clearTimeout(toastWrap._hideTimeout);
    toastWrap._hideTimeout = setTimeout(() => {
      toastInner.classList.remove('toast-show');
      toastInner.classList.add('toast-hide');
      setTimeout(() => toastWrap.classList.add('hidden'), 400);
    }, duration);
  }

  //Bookings Panel (infinite scroll + cards)
  const panel = document.getElementById('bookings-panel');
  const list = document.getElementById('bookings-list');
  const loading = document.getElementById('bookings-loading');
  const endMsg = document.getElementById('bookings-end');

  // Default config
  let LIMIT = 12;
  let DEFAULT_IMAGE = '/static/images/No_Image_Available.jpg';
  let CAL_ICON = '/static/images/calendar.png';
  let CLOCK_ICON = '/static/images/clock.png';

  if (panel) {
    LIMIT = safeParseInt(panel.dataset.limit, 12);
    DEFAULT_IMAGE = panel.dataset.defaultImage || DEFAULT_IMAGE;
    CAL_ICON = panel.dataset.calendarIcon || CAL_ICON;
    CLOCK_ICON = panel.dataset.clockIcon || CLOCK_ICON;
  }

  // Render a single booking card
  function renderCard(item) {
    const title = item.title || item.name || item.venue_name || item.venue || item.court || 'Booking';
    const dateRaw = item.date || item.booking_date || '';
    const date = dateRaw
      ? new Date(dateRaw).toLocaleDateString(undefined, {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })
      : '';
    const start = item.start_time || '';
    const end = item.end_time || '';
    const location = item.location || item.venue_name || '';
    const price = item.total_price ? 'Rp ' + item.total_price : '';
    const image = item.venue_image || item.thumbnail || item.image_url || DEFAULT_IMAGE;

    return `
      <div data-id="${item.id}" class="bg-gradient-to-r from-white/40 to-white/25 backdrop-blur rounded-xl shadow-lg border border-white/40 p-4 animate-fade-up">
        <div class="flex gap-4 items-center">
          <div class="flex-shrink-0 w-32 h-32 rounded-lg overflow-hidden border-2 border-white/50 shadow-sm">
            <img src="${image}" alt="${title}" class="w-full h-full object-cover">
          </div>

          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-500">${location}</div>
            <div class="font-bold text-lg text-gray-800 truncate">${title}</div>
            <div class="text-sm text-gray-600 mt-2 flex items-center gap-6">
              <div class="flex items-center gap-2">
                <img src="${CAL_ICON}" alt="Date" class="w-5 h-5 opacity-80">
                <span>${date}</span>
              </div>
              <div class="flex items-center gap-2">
                <img src="${CLOCK_ICON}" alt="Time" class="w-5 h-5 opacity-80">
                <span>${start}${end ? ' - ' + end : ''}</span>
              </div>
            </div>
            <div class="mt-3 text-sm text-gray-700">${price}</div>
          </div>
        </div>
      </div>
    `;
  }

  window._bookingPanel = { renderCard };

  // --- Infinite loading state
  let offset = 0;
  let loadingMore = false;
  let hasMore = true;

  async function loadMore() {
    if (!panel || loadingMore || !hasMore) return;
    loadingMore = true;
    if (loading) loading.classList.remove('hidden');
    try {
      const resp = await fetch(
        window.location.pathname + `?type=bookings&offset=${offset}&limit=${LIMIT}`,
        {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          credentials: 'same-origin',
        }
      );
      if (!resp.ok) throw new Error('Network error');
      const data = await resp.json();
      if (data && data.success) {
        const items = data.items || [];
        for (const it of items) {
          const node = document.createElement('div');
          node.innerHTML = renderCard(it);
          list.appendChild(node.firstElementChild);
        }
        offset += items.length;
        hasMore = !!data.has_more;
        if (!hasMore && endMsg) endMsg.classList.remove('hidden');
      } else {
        console.error('Server error loading bookings', data);
      }
    } catch (err) {
      console.error('Loading bookings failed', err);
    } finally {
      loadingMore = false;
      if (loading) loading.classList.add('hidden');
    }
  }

  if (panel) {
    loadMore();
    panel.addEventListener('scroll', function () {
      const threshold = 200;
      if (panel.scrollTop + panel.clientHeight >= panel.scrollHeight - threshold) {
        loadMore();
      }
    });
  }

  // Profile Edit Modal and Submit
  const editBtnProfile = document.getElementById('edit-profile-btn');
  const editModal = document.getElementById('edit-profile-modal');
  const editCloseBtn = document.getElementById('edit-profile-close');
  const editForm = document.getElementById('edit-profile-form');
  const editAlert = document.getElementById('edit-profile-alert');

  const inUsername = document.getElementById('ep-username');
  const inName = document.getElementById('ep-name');
  const inNumber = document.getElementById('ep-number');
  const inProfilePicture = document.getElementById('ep-profile_picture');

  function clearEditErrors() {
    document.querySelectorAll('.ep-err').forEach((el) => {
      el.textContent = '';
      el.classList.add('hidden');
    });
    if (editAlert) {
      editAlert.classList.add('hidden');
      editAlert.textContent = '';
      editAlert.className = 'hidden';
    }
  }

  function showErrors(errors) {
    clearEditErrors();
    for (const [field, msgs] of Object.entries(errors || {})) {
      const el = document.querySelector(`.ep-err[data-field="${field}"]`);
      if (el) {
        el.textContent = msgs.join(' ');
        el.classList.remove('hidden');
      }
    }
  }

  function openProfileModal() {
    if (!editBtnProfile || !editModal) return;
    inUsername.value = editBtnProfile.dataset.username || '';
    inName.value = editBtnProfile.dataset.name || '';
    inNumber.value = editBtnProfile.dataset.number || '';
    inProfilePicture.value = editBtnProfile.dataset.profile_picture || '';
    clearEditErrors();
    if (editAlert) editAlert.classList.add('hidden');
    editModal.classList.remove('hidden');
    inUsername && inUsername.focus();
  }

  function closeProfileModal() {
    if (!editModal) return;
    editModal.classList.add('hidden');
  }

  function formatPhone(input) {
    if (!input) return '';
    let digits = String(input).replace(/\D/g, '');
    if (digits.startsWith('0')) digits = '62' + digits.slice(1);
    else if (digits.startsWith('+')) digits = digits.replace(/^\+/, '');
    else if (!digits.startsWith('62')) {
      if (digits.length <= 12) digits = '62' + digits;
    }
    if (!digits.startsWith('62')) digits = '62' + digits;

    const rest = digits.slice(2);
    if (!rest) return '+62';
    const a = rest.slice(0, 3);
    const b = rest.slice(3, 7);
    const c = rest.slice(7);
    let out = '+62 ' + a;
    if (b) out += '-' + b;
    if (c) out += '-' + c;
    return out;
  }

  async function submitProfileForm(ev) {
    ev.preventDefault();
    clearEditErrors();
    if (!editForm) return;

    const data = new URLSearchParams();
    data.append('username', inUsername.value.trim());
    data.append('name', inName.value.trim());
    data.append('number', inNumber.value.trim());
    data.append('profile_picture', inProfilePicture.value.trim());

    const editUrl = editBtnProfile && editBtnProfile.dataset.editUrl;
    if (!editUrl) {
      console.error('Edit profile URL not provided as data-edit-url on button.');
      return;
    }

    let resp;
    try {
      resp = await fetch(editUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': CSRF_TOKEN,
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        },
        body: data.toString(),
        credentials: 'same-origin',
      });
    } catch (err) {
      if (editAlert) {
        editAlert.className =
          'mb-4 p-3 rounded text-sm bg-red-50 border border-red-200 text-red-700';
        editAlert.textContent = 'Network error. Please try again.';
        editAlert.classList.remove('hidden');
      }
      return;
    }

    if (resp.ok) {
      const json = await resp.json().catch(() => null);
      if (!json) {
        if (editAlert) {
          editAlert.className =
            'mb-4 p-3 rounded text-sm bg-red-50 border border-red-200 text-red-700';
          editAlert.textContent = 'Unexpected server response.';
          editAlert.classList.remove('hidden');
        }
        return;
      }

      editBtnProfile.dataset.username = json.username || editBtnProfile.dataset.username;
      editBtnProfile.dataset.name = json.name || editBtnProfile.dataset.name;
      editBtnProfile.dataset.role = json.role || editBtnProfile.dataset.role;
      editBtnProfile.dataset.number = json.number || editBtnProfile.dataset.number;
      editBtnProfile.dataset.profile_picture =
        json.profile_picture || editBtnProfile.dataset.profile_picture;

      const nameEl = document.querySelector('.profile-fullname');
      if (nameEl) nameEl.textContent = json.name || nameEl.textContent;

      const roleEl = document.querySelector('.profile-role');
      if (roleEl)
        roleEl.textContent = json.role
          ? json.role.charAt(0).toUpperCase() + json.role.slice(1)
          : roleEl.textContent;

      const avatarImg = document.querySelector('.profile-avatar');
      if (avatarImg && json.profile_picture) avatarImg.src = json.profile_picture;

      (function updatePhoneDisplay() {
        const phoneEl = document.getElementById('profile-number');
        if (!phoneEl) return;
        let formatted = json.formatted_number || json.formatted || null;
        let raw = json.number || json.raw_number || null;
        if (!formatted && raw) formatted = formatPhone(raw);
        if (formatted) {
          phoneEl.textContent = formatted;
          if (raw) phoneEl.setAttribute('data-raw', raw);
        }
      })();

      document.dispatchEvent(new Event('dashboard:recalculate_heights'));
      showToast('Profile Updated!', { duration: 2200 });
      setTimeout(() => closeProfileModal(), 700);
    } else {
      const err = await resp.json().catch(() => null);
      if (err && err.errors) {
        showErrors(err.errors);
      } else if (editAlert) {
        editAlert.className =
          'mb-4 p-3 rounded text-sm bg-red-50 border border-red-200 text-red-700';
        editAlert.textContent =
          (err && err.error) || 'An unexpected error occurred.';
        editAlert.classList.remove('hidden');
      }
    }
  }

  if (editBtnProfile) editBtnProfile.addEventListener('click', openProfileModal);
  if (editCloseBtn) editCloseBtn.addEventListener('click', closeProfileModal);
  if (editForm) editForm.addEventListener('submit', submitProfileForm);
  if (editModal)
    editModal.addEventListener('click', (e) => {
      if (e.target === editModal) closeProfileModal();
    });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && editModal && !editModal.classList.contains('hidden'))
      closeProfileModal();
  });

  // Profile Delete
  const deleteBtn = document.getElementById('delete-profile-btn');
  const confirmModal = document.getElementById('delete-confirm-modal');
  const yesBtn = document.getElementById('confirm-delete-yes');
  const noBtn = document.getElementById('confirm-delete-no');

  function openConfirm() {
    if (confirmModal) confirmModal.classList.remove('hidden');
  }
  function closeConfirm() {
    if (confirmModal) confirmModal.classList.add('hidden');
  }

  if (deleteBtn) deleteBtn.addEventListener('click', openConfirm);
  if (noBtn) noBtn.addEventListener('click', closeConfirm);

  async function performDelete(ev) {
    ev.preventDefault();
    if (!yesBtn || !deleteBtn) return;
    yesBtn.disabled = true;
    if (noBtn) noBtn.disabled = true;

    const deleteUrl = deleteBtn.dataset.deleteUrl;
    if (!deleteUrl) {
      alert('Delete endpoint not configured.');
      yesBtn.disabled = false;
      if (noBtn) noBtn.disabled = false;
      return;
    }

    try {
      const resp = await fetch(deleteUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': CSRF_TOKEN,
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json',
        },
        credentials: 'same-origin',
      });

      if (!resp.ok) {
        let err = null;
        try {
          err = await resp.json();
        } catch (e) {}
        alert(
          (err && err.error) || `Delete failed (status ${resp.status})`
        );
        yesBtn.disabled = false;
        if (noBtn) noBtn.disabled = false;
        return;
      }

      const json = await resp.json().catch(() => null);
      if (json && json.success) {
        window.location.href = json.redirect || '/';
      } else {
        alert((json && json.error) || 'Delete failed');
        yesBtn.disabled = false;
        if (noBtn) noBtn.disabled = false;
      }
    } catch (err) {
      console.error('Delete error', err);
      alert('Network error, try again.');
      yesBtn.disabled = false;
      if (noBtn) noBtn.disabled = false;
    }
  }

  if (yesBtn) yesBtn.addEventListener('click', performDelete);
  if (confirmModal)
    confirmModal.addEventListener('click', (e) => {
      if (e.target === confirmModal) closeConfirm();
    });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && confirmModal && !confirmModal.classList.contains('hidden'))
      closeConfirm();
  });

  window._bookingPanel.loadMore = loadMore;
})();
