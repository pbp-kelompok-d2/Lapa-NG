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
    const title = item.name || item.title || 'Unnamed';
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
  }

  // --- Initialize both panels ---
  const bookingsPanel = document.getElementById('bookings-panel');
  const bookingsList = document.getElementById('bookings-list');
  if (bookingsPanel && bookingsList)
    initAjaxPanel(bookingsPanel, bookingsList, 'bookings');

  const courtsPanel = document.getElementById('courts-panel');
  const courtsList = document.getElementById('courts-list');
  if (courtsPanel && courtsList)
    initAjaxPanel(courtsPanel, courtsList, 'my_courts');

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
    });

    tabCourts.addEventListener('click', () => {
      tabCourts.classList.add('bg-white', 'text-green-600');
      tabCourts.classList.remove('bg-white/30', 'text-gray-700');
      tabBookings.classList.add('bg-white/30', 'text-gray-700');
      tabBookings.classList.remove('bg-white', 'text-green-600');
      courtsPanel.classList.remove('hidden');
      bookingsPanel.classList.add('hidden');
      title.textContent = 'My Courts';
    });
  }
})();
