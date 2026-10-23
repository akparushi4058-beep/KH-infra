/* ============================================================
   KH Infra Equipment — homepage catalogue
   Product data comes from catalog.json, inlined into index.html by build.py
   ============================================================ */
const KH = JSON.parse(document.getElementById('catalog-data').textContent);
const PRODUCTS = KH.products;
const CATS = [{ id: 'all', label: 'All', icon: '/favicon-192.png' }, ...KH.categories];
const WA_NUMBER = '918386055533';
let activeCat = 'all';

function renderCats() {
  document.getElementById('cats').innerHTML = CATS.map(c => `
    <a class="cat-item ${c.id === activeCat ? 'on' : ''}" href="${c.slug ? '/' + c.slug + '/' : '/#catalog'}" data-cat="${c.id}">
      <span class="ic ${c.photo ? 'photo' : ''}"><img src="${c.icon}" alt="" loading="lazy" /></span>
      <span class="lb">${c.label}</span>
    </a>
  `).join('');
}
function cardHtml(p) {
  return `
    <a class="p" href="/${p.slug}/" data-slug="${p.slug}">
      <div class="ph">
        <span class="tr">↗</span>
        <img class="fill" src="${p.images[0]}" alt="" aria-hidden="true" loading="lazy" />
        <img src="${p.images[0]}" alt="${p.name}" loading="lazy" />
      </div>
      <div class="info"><div class="row"><div class="name">${p.name}</div></div></div>
    </a>`;
}
function renderGrid() {
  const list = activeCat === 'all' ? PRODUCTS : PRODUCTS.filter(p => p.cat === activeCat);
  document.getElementById('grid').innerHTML = list.map(cardHtml).join('');
}

// Category bar and footer links filter the catalogue in place; product cards open the product sheet
document.addEventListener('click', e => {
  if (e.metaKey || e.ctrlKey || e.shiftKey) return;
  const card = e.target.closest('.p[data-slug]');
  if (card) {
    e.preventDefault();
    openModal(PRODUCTS.find(p => p.slug === card.dataset.slug));
    return;
  }
  const t = e.target.closest('[data-cat]');
  if (!t) return;
  e.preventDefault();
  activeCat = t.dataset.cat; renderCats(); renderGrid();
  document.querySelector('#cats .on')?.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' });
  const top = document.getElementById('grid').getBoundingClientRect().top + scrollY - navHeight() - document.getElementById('cats').offsetHeight - 24;
  if (scrollY > top) window.scrollTo({ top, behavior: 'smooth' });
});

// The category bar sticks just under the header, whose height changes by screen size
function navHeight() { return document.querySelector('.nav').offsetHeight; }
function syncNavHeight() { document.documentElement.style.setProperty('--nav-h', navHeight() + 'px'); }
addEventListener('resize', syncNavHeight);
syncNavHeight();

/* ============================================================
   PRODUCT SHEET
   ============================================================ */
const M = {
  el: document.getElementById('modal'), sheet: document.getElementById('sheet'),
  track: document.getElementById('mTrack'), thumbs: document.getElementById('mThumbs'),
  count: document.getElementById('mCount'),
  info: document.getElementById('mInfo'),
};
const productUrl = p => `${location.origin}/${p.slug}/`;
const catLabel = id => (CATS.find(c => c.id === id) || {}).label || '';
let CUR = null, sheetInHistory = false;

function openModal(p) {
  if (!p) return;
  CUR = p;
  const media = [...p.images.map(src => ({ src })), ...(p.videos || []).map(v => ({ ...v, video: true }))];
  M.track.innerHTML = media.map((m, i) => m.video
    ? `<video src="${m.src}" poster="${m.poster}" controls playsinline preload="none"></video>`
    : `<img src="${m.src}" alt="${p.name} – photo ${i + 1}" onclick="openViewer(this.src)" />`).join('');
  // Small photos under the main one: tap to jump to that photo or video
  M.thumbs.innerHTML = media.length > 1 ? media.map((m, i) =>
    `<button type="button" class="${i ? '' : 'on'}${m.video ? ' vid' : ''}" onclick="goTo(${i})" aria-label="${m.video ? 'Video' : 'Photo ' + (i + 1)}"><img src="${m.video ? m.poster : m.src}" alt="" loading="lazy" /></button>`).join('') : '';
  document.getElementById('mCat').textContent = catLabel(p.cat);
  document.getElementById('mName').textContent = p.name;
  document.getElementById('mDesc').textContent = p.desc || '';
  document.getElementById('mSpecs').innerHTML = Object.entries(p.specs).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
  document.getElementById('mShareLbl').textContent = 'Share this machine';
  const msg = `Hi KH Infra Equipment, I'm interested in the ${p.name}. Please share price and availability.\n${productUrl(p)}`;
  document.getElementById('mWa').href = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(msg)}`;
  M.sheet.style.transform = '';
  M.el.classList.add('show'); M.el.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  M.track.scrollLeft = 0; M.info.scrollTop = 0;
  updateArrows();
  // The address bar shows the product's own page, and the phone's back button closes the sheet
  history.pushState({ product: p.slug }, '', `/${p.slug}/`);
  sheetInHistory = true;
}
function pauseVideos() { M.track.querySelectorAll('video').forEach(v => v.pause()); }
function hideSheet() {
  pauseVideos();
  M.el.classList.remove('show'); M.el.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = ''; CUR = null;
}
function closeModal() {
  if (!M.el.classList.contains('show')) return;
  if (sheetInHistory) history.back(); else hideSheet();
}
addEventListener('popstate', () => {
  sheetInHistory = false;
  closeViewer();
  if (M.el.classList.contains('show')) hideSheet();
});
M.el.addEventListener('click', e => { if (e.target === M.el) closeModal(); });
document.addEventListener('keydown', e => {
  if (e.key !== 'Escape') return;
  if (document.getElementById('viewer').classList.contains('show')) closeViewer(); else closeModal();
});

// Gallery: swipe on phones, arrows on desktop, dots follow the current photo
function current() { return Math.round(M.track.scrollLeft / (M.track.clientWidth || 1)); }
function goTo(i) { M.track.scrollTo({ left: i * M.track.clientWidth, behavior: 'smooth' }); }
function slide(dir) { goTo(current() + dir); }
function updateArrows() {
  const n = M.track.children.length, i = current();
  document.querySelector('.m-arrow.prev').hidden = n < 2 || i === 0;
  document.querySelector('.m-arrow.next').hidden = n < 2 || i === n - 1;
  M.count.textContent = n > 1 ? `${i + 1} / ${n}` : '';
  [...M.thumbs.children].forEach((b, k) => b.classList.toggle('on', k === i));
  M.thumbs.children[i]?.scrollIntoView({ inline: 'nearest', block: 'nearest' });
}
M.track.addEventListener('scroll', () => { pauseVideos(); requestAnimationFrame(updateArrows); }, { passive: true });

// Phones: swipe down on the photos or the top of the details to close the sheet
let dragY = null;
M.sheet.addEventListener('touchstart', e => {
  const fromTop = e.target.closest('.m-stage') || (e.target.closest('.m-info') && M.info.scrollTop === 0);
  dragY = fromTop ? e.touches[0].clientY : null;
}, { passive: true });
M.sheet.addEventListener('touchmove', e => {
  if (dragY === null) return;
  const dy = e.touches[0].clientY - dragY;
  if (dy > 0 && M.info.scrollTop === 0) M.sheet.style.transform = `translateY(${dy}px)`;
}, { passive: true });
M.sheet.addEventListener('touchend', e => {
  if (dragY === null) return;
  const dy = e.changedTouches[0].clientY - dragY; dragY = null;
  M.sheet.style.transition = 'transform .2s';
  M.sheet.style.transform = dy > 120 ? 'translateY(100%)' : '';
  setTimeout(() => { M.sheet.style.transition = ''; if (dy > 120) closeModal(); }, 200);
});

// Full-screen photo (pinch to zoom on phones)
function openViewer(src) { document.getElementById('vImg').src = src; document.getElementById('viewer').classList.add('show'); }
function closeViewer() { document.getElementById('viewer').classList.remove('show'); }

async function shareProduct() {
  if (!CUR) return;
  const url = productUrl(CUR), title = CUR.name;
  if (navigator.share) { try { await navigator.share({ title, text: `${title} – KH Infra Equipment`, url }); } catch {} return; }
  try { await navigator.clipboard.writeText(url); document.getElementById('mShareLbl').textContent = 'Link copied'; }
  catch { window.open(`https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`, '_blank'); }
}

// Old shared links (khgroupindia.com/#bar-bending-machine-gw42) now go to the product's own page
function redirectOldLink() {
  const id = decodeURIComponent(location.hash.slice(1));
  const p = id && PRODUCTS.find(x => x.slug === id || (x.old_slugs || []).includes(id));
  if (p) location.replace(`/${p.slug}/`);
}
addEventListener('hashchange', redirectOldLink);

/* GA4 click tracking — phone, WhatsApp, email, product views */
document.addEventListener('click', function(e) {
  if (typeof gtag !== 'function') return;
  const a = e.target.closest('a');
  if (a) {
    const href = a.getAttribute('href') || '';
    if (href.startsWith('tel:')) {
      gtag('event', 'phone_click', { event_category: 'contact', event_label: href.replace('tel:', '') });
    } else if (href.includes('wa.me')) {
      gtag('event', 'whatsapp_click', { event_category: 'contact', event_label: a.textContent.trim().slice(0, 40) || 'whatsapp' });
    } else if (href.startsWith('mailto:')) {
      gtag('event', 'email_click', { event_category: 'contact', event_label: href.replace('mailto:', '') });
    }
  }
  const card = e.target.closest('.p[data-slug]');
  if (card) gtag('event', 'product_view', { event_category: 'catalog', event_label: card.dataset.slug });
});

/* INIT */
redirectOldLink();
renderCats();
renderGrid();
