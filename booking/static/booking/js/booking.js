function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}
const csrftoken = getCookie('csrftoken');

async function jsonGET(url) {
  const res = await fetch(url, { headers: { 'Accept': 'application/json' }});
  return res.json();
}
async function jsonPOST(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'Accept': 'application/json' },
    body: JSON.stringify(body || {})
  });
  return res.json().then(data => ({ status: res.status, data }));
}

async function loadBookings() {
  const data = await jsonGET('/booking/api/list/');
  renderBookings(data.bookings || []);
}
function renderBookings(items) {
  const el = document.getElementById('booking-list');
  el.innerHTML = '';
  if (!items.length) {
    el.innerHTML = '<p class="text-gray-500">No bookings yet.</p>';
    return;
  }
  for (const b of items) {
    const row = document.createElement('div');
    row.className = 'border rounded p-3';
    row.innerHTML = `
      <div class="font-semibold">${b.venue_name}</div>
      <div class="text-sm text-gray-700">${b.date} | ${b.start_time}–${b.end_time}</div>
      ${b.notes ? `<div class="text-sm text-gray-500">${b.notes}</div>` : ''}
    `;
    el.appendChild(row);
  }
}

async function searchVenues() {
  const q = document.getElementById('q').value.trim();
  const sport = document.getElementById('sport').value.trim();
  const loc = document.getElementById('loc').value.trim();
  const data = await jsonGET(`/booking/api/search/?q=${encodeURIComponent(q)}&sport=${encodeURIComponent(sport)}&loc=${encodeURIComponent(loc)}`);
  renderSearch(data.venues || []);
}
function renderSearch(items) {
  const el = document.getElementById('search-results');
  el.innerHTML = '';
  if (!items.length) {
    el.innerHTML = '<p class="text-gray-500">No venues found.</p>';
    return;
  }
  for (const v of items) {
    const row = document.createElement('div');
    row.className = 'border rounded p-3 flex justify-between items-center';
    row.innerHTML = `
      <div class="font-semibold">${v.name}</div>
      <button class="bg-rose-600 text-white px-3 py-1 rounded">Book Now</button>
    `;
    row.querySelector('button').addEventListener('click', async () => {
      // Minimal: booking hari ini 08:00–09:00. Nanti di Iterasi 2 pakai date-time picker.
      const today = new Date().toISOString().slice(0,10);
      const { status, data } = await jsonPOST('/booking/api/from-main/', {
        venue_id: v.id,
        date: today,
        start_time: '08:00',
        end_time: '09:00',
        notes: ''
      });
      if (status >= 200 && status < 300 && data.ok) {
        await loadBookings();
      } else {
        alert('Failed to book.');
      }
    });
    el.appendChild(row);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadBookings();
  document.getElementById('btn-search').addEventListener('click', searchVenues);
});
