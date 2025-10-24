(function () {
  // --- Utilities ---
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

  // --- Global defaults for icons & images ---
  let DEFAULT_IMAGE = '/static/images/No_Image_Available.jpg';
  let CAL_ICON = '/static/images/calendar.png';
  let CLOCK_ICON = '/static/images/clock.png';

  function renderCard(item) {
    const title = item.name || item.title || item.venue_name || 'Unnamed';
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
    const price =
      item.total_price && !isNaN(item.total_price)
        ? 'Rp ' + Number(item.total_price).toLocaleString('id-ID')
        : '';
    const image =
      item.venue_image ||
      item.thumbnail ||
      item.image_url ||
      item.image ||
      DEFAULT_IMAGE;

    return `
      <div class="bg-white/30 backdrop-blur-md border border-white/40 rounded-xl shadow p-4 flex gap-4 items-center animate-fade-up">
        <div class="w-28 h-28 flex-shrink-0 overflow-hidden rounded-lg border border-white/50 shadow-sm">
          <img src="${image}" alt="${title}" class="w-full h-full object-cover" onerror="this.onerror=null;this.src='${DEFAULT_IMAGE}'">
        </div>
        <div class="flex-1 min-w-0">
          ${location ? `<div class="text-sm text-gray-500">${location}</div>` : ''}
          <div class="font-bold text-lg text-gray-800 truncate">${title}</div>
          ${
            date || start
              ? `
            <div class="text-sm text-gray-600 mt-2 flex flex-col sm:flex-row sm:items-center sm:gap-6">
              ${
                date
                  ? `<div class="flex items-center gap-2"><img src="${CAL_ICON}" class="w-5 h-5 opacity-80"><span>${date}</span></div>`
                  : ''
              }
              ${
                start
                  ? `<div class="flex items-center gap-2"><img src="${CLOCK_ICON}" class="w-5 h-5 opacity-80"><span>${start}${
                      end ? ' - ' + end : ''
                    }</span></div>`
                  : ''
              }
            </div>`
              : ''
          }
          ${price ? `<div class="mt-3 text-sm text-gray-700">${price}</div>` : ''}
        </div>
      </div>`;
  }

  // --- Panel Loader (shared for Bookings & My Courts) ---
  function initAjaxPanel(panelEl, listEl, type) {
    let offset = 0;
    let loading = false;
    let hasMore = true;
    const limit = safeParseInt(panelEl.dataset.limit, 12);
    const loadingEl = document.getElementById(`${type}-loading`);
    const endEl = document.getElementById(`${type}-end`);

    async function loadMore() {
      if (loading || !hasMore) return;
      loading = true;
      if (loadingEl) loadingEl.classList.remove('hidden');
      try {
        const resp = await fetch(
          `${window.location.pathname}?type=${type}&offset=${offset}&limit=${limit}`,
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
            const div = document.createElement('div');
            div.innerHTML = renderCard(it);
            listEl.appendChild(div.firstElementChild);
          }
          offset += items.length;
          hasMore = !!data.has_more;
          if (!hasMore && endEl) endEl.classList.remove('hidden');
        } else {
          console.error('Server error', data);
        }
      } catch (err) {
        console.error('Load failed', err);
      } finally {
        loading = false;
        if (loadingEl) loadingEl.classList.add('hidden');
      }
    }

    // initial load
    loadMore();

    // infinite scroll
    panelEl.addEventListener('scroll', () => {
      const threshold = 200;
      if (
        panelEl.scrollTop + panelEl.clientHeight >=
        panelEl.scrollHeight - threshold
      ) {
        loadMore();
      }
    });

    // expose loader for debugging if needed
    return { loadMore };
  }

  // --- Initialize both panels ---
  const bookingsPanel = document.getElementById('bookings-panel');
  const bookingsList = document.getElementById('bookings-list');
  if (bookingsPanel && bookingsList) {
    window._bookingPanel = window._bookingPanel || {};
    window._bookingPanel.bookings = initAjaxPanel(bookingsPanel, bookingsList, 'bookings');
  }

  const courtsPanel = document.getElementById('courts-panel');
  const courtsList = document.getElementById('courts-list');
  if (courtsPanel && courtsList) {
    window._bookingPanel = window._bookingPanel || {};
    window._bookingPanel.myCourts = initAjaxPanel(courtsPanel, courtsList, 'my_courts');
  }

  // --- Tab Switching ---
  const tabBookings = document.getElementById('tab-bookings');
  const tabCourts = document.getElementById('tab-courts');
  const title = document.getElementById('dashboard-title');

  if (tabBookings && tabCourts && bookingsPanel && courtsPanel) {
    tabBookings.addEventListener('click', () => {
      tabBookings.classList.add('bg-white', 'text-green-600');
      tabBookings.classList.remove('bg-white/30', 'text-gray-700');
      tabCourts.classList.add('bg-white/30', 'text-gray-700');
      tabCourts.classList.remove('bg-white', 'text-green-600');
      bookingsPanel.classList.remove('hidden');
      courtsPanel.classList.add('hidden');
      title.textContent = 'Booked Courts';
      // recalc heights if needed
      document.dispatchEvent(new Event('dashboard:recalculate_heights'));
    });

    tabCourts.addEventListener('click', () => {
      tabCourts.classList.add('bg-white', 'text-green-600');
      tabCourts.classList.remove('bg-white/30', 'text-gray-700');
      tabBookings.classList.add('bg-white/30', 'text-gray-700');
      tabBookings.classList.remove('bg-white', 'text-green-600');
      courtsPanel.classList.remove('hidden');
      bookingsPanel.classList.add('hidden');
      title.textContent = 'My Courts';
      // recalc heights if needed
      document.dispatchEvent(new Event('dashboard:recalculate_heights'));
    });
  }

  // --- EDIT PROFILE UI & AJAX ---
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
    editModal.classList.add('flex');
    inUsername && inUsername.focus();
  }

  function closeProfileModal() {
    if (!editModal) return;
    editModal.classList.add('hidden');
    editModal.classList.remove('flex');
  }

  // phone formatting helper (fallback display)
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

      // update dataset values on the edit button so next open is correct
      editBtnProfile.dataset.username = json.username || editBtnProfile.dataset.username;
      editBtnProfile.dataset.name = json.name || editBtnProfile.dataset.name;
      editBtnProfile.dataset.role = json.role || editBtnProfile.dataset.role;
      editBtnProfile.dataset.number = json.number || editBtnProfile.dataset.number;
      editBtnProfile.dataset.profile_picture =
        json.profile_picture || editBtnProfile.dataset.profile_picture;

      // update visible DOM fields
      const nameEl = document.querySelector('.profile-fullname');
      if (nameEl) nameEl.textContent = json.name || nameEl.textContent;

      const roleEl = document.querySelector('.profile-role');
      if (roleEl)
        roleEl.textContent = json.role
          ? json.role.charAt(0).toUpperCase() + json.role.slice(1)
          : roleEl.textContent;

      const avatarImg = document.querySelector('.profile-avatar');
      if (avatarImg && json.profile_picture) avatarImg.src = json.profile_picture;

      // update phone display
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

      // recalc heights if needed (your code listens for this)
      document.dispatchEvent(new Event('dashboard:recalculate_heights'));

      // show toast & success message
      const toastWrap = document.getElementById('global-toast');
      const toastInner = document.getElementById('global-toast-inner');
      const toastMsg = document.getElementById('global-toast-message');
      if (toastMsg) toastMsg.textContent = json.message || 'Profile updated successfully.';
      if (typeof window !== 'undefined' && window.getComputedStyle) {
        if (toastWrap) toastWrap.classList.remove('hidden');
        if (toastInner) {
          toastInner.classList.remove('toast-hide');
          toastInner.classList.add('toast-show');
        }
        clearTimeout(toastWrap._hideTimeout);
        toastWrap._hideTimeout = setTimeout(() => {
          if (toastInner) {
            toastInner.classList.remove('toast-show');
            toastInner.classList.add('toast-hide');
          }
          setTimeout(() => { if (toastWrap) toastWrap.classList.add('hidden'); }, 400);
        }, 2200);
      }

      if (editAlert) {
        editAlert.className =
          'mb-4 p-3 rounded text-sm bg-green-50 border border-green-200 text-green-700';
        editAlert.textContent = json.message || 'Saved';
        editAlert.classList.remove('hidden');
      }

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

  // Wire up edit modal open/close/submit
  if (editBtnProfile) editBtnProfile.addEventListener('click', openProfileModal);
  if (editCloseBtn) editCloseBtn.addEventListener('click', closeProfileModal);
  if (editForm) editForm.addEventListener('submit', submitProfileForm);
  if (editModal) editModal.addEventListener('click', function (e) {
    if (e.target === editModal) closeProfileModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && editModal && !editModal.classList.contains('hidden')) closeProfileModal();
  });

  // --- DELETE PROFILE ---
  const deleteBtn = document.getElementById('delete-profile-btn');
  const confirmModal = document.getElementById('delete-confirm-modal');
  const yesBtn = document.getElementById('confirm-delete-yes');
  const noBtn = document.getElementById('confirm-delete-no');

  function openConfirm() {
    if (confirmModal) {
      confirmModal.classList.remove('hidden');
      confirmModal.classList.add('flex');
    }
  }
  function closeConfirm() {
    if (confirmModal) {
      confirmModal.classList.add('hidden');
      confirmModal.classList.remove('flex');
    }
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
          'Accept': 'application/json'
        },
        credentials: 'same-origin',
        body: '' // some endpoints accept empty POST body for AJAX delete
      });

      if (!resp.ok) {
        let err = null;
        try { err = await resp.json(); } catch (e) {}
        const msg = (err && err.error) ? err.error : `Delete failed (status ${resp.status})`;
        alert(msg);
        yesBtn.disabled = false;
        if (noBtn) noBtn.disabled = false;
        return;
      }

      const json = await resp.json().catch(() => null);
      if (json && json.success) {
        // redirect to provided url or home
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
  if (confirmModal) confirmModal.addEventListener('click', function (e) {
    if (e.target === confirmModal) closeConfirm();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && confirmModal && !confirmModal.classList.contains('hidden')) closeConfirm();
  });

  // --- Equal Heights (keeps left and right equal) ---
  function recalcHeights() {
    try {
      const left = document.getElementById('left-card');
      const right = document.getElementById('right-card');
      if (!left || !right) return;
      left.style.minHeight = '';
      right.style.minHeight = '';
      const leftRect = left.getBoundingClientRect();
      const rightRect = right.getBoundingClientRect();
      const maxH = Math.max(leftRect.height, rightRect.height);
      left.style.minHeight = maxH + 'px';
      right.style.minHeight = maxH + 'px';
    } catch (e) {
      // ignore
    }
  }

  window.addEventListener('load', recalcHeights);
  window.addEventListener('resize', recalcHeights);
  document.addEventListener('dashboard:recalculate_heights', recalcHeights);

  // expose for debugging
  window._bookingPanel = window._bookingPanel || {};
  window._bookingPanel.loadMore = function () {
    if (window._bookingPanel.bookings && window._bookingPanel.bookings.loadMore) window._bookingPanel.bookings.loadMore();
    if (window._bookingPanel.myCourts && window._bookingPanel.myCourts.loadMore) window._bookingPanel.myCourts.loadMore();
  };
})();
