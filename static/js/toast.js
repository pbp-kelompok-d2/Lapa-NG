function showToast(title, message, type = 'normal', duration = 3000) {
  const el = document.getElementById('toast-component');
  const t = document.getElementById('toast-title');
  const m = document.getElementById('toast-message');
  if (!el) return;

  // reset class dasar
  el.classList.remove(
    'bg-red-50','border-red-500','text-red-600',
    'bg-green-50','border-green-500','text-green-600',
    'bg-white','border-gray-300','text-gray-800'
  );

  // set berdasar tipe
  if (type === 'success') {
    el.classList.add('bg-green-50','border-green-500','text-green-600');
    el.style.border = '1px solid #22c55e';
  } else if (type === 'error') {
    el.classList.add('bg-red-50','border-red-500','text-red-600');
    el.style.border = '1px solid #ef4444';
  } else {
    el.classList.add('bg-white','border-gray-300','text-gray-800');
    el.style.border = '1px solid #d1d5db';
  }

  t.textContent = title || '';
  m.textContent = message || '';

  el.classList.remove('opacity-0','translate-y-64');
  el.classList.add('opacity-100','translate-y-0');

  window.clearTimeout(el._hideTimer);
  el._hideTimer = window.setTimeout(() => {
    el.classList.remove('opacity-100','translate-y-0');
    el.classList.add('opacity-0','translate-y-64');
  }, duration);
}
