/* global QWebChannel */

function setStatus(text) {
  const el = document.getElementById('status');
  if (el) el.textContent = text;
}

function setSelectedFolder(text) {
  const el = document.getElementById('selectedFolder');
  if (el) el.textContent = text || '(none)';
}

function ensurePosterObserver() {
  if (gPosterObserver) return;
  gPosterObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target;
        const path = el.getAttribute('data-video-path');
        if (!path) continue;
        if (gPosterRequested.has(path)) {
          gPosterObserver.unobserve(el);
          continue;
        }
        gPosterRequested.add(path);

        if (gBridge && gBridge.get_video_poster) {
          gBridge.get_video_poster(path, function (posterUrl) {
            if (posterUrl) {
              el.src = posterUrl;
            } else {
              el.removeAttribute('src');
              if (gBridge.debug_video_poster) {
                gBridge.debug_video_poster(path, function (info) {
                  console.log('debug_video_poster', info);
                });
              }
            }
          });
        }

        gPosterObserver.unobserve(el);
      }
    },
    {
      // Start loading slightly before visible so scrolling feels instant.
      root: null,
      rootMargin: '600px 0px 600px 0px',
      threshold: 0.01,
    }
  );
}

function resetPosterState() {
  gPosterRequested.clear();
  if (gPosterObserver) {
    gPosterObserver.disconnect();
    gPosterObserver = null;
  }
}

let gLoadingShownAt = 0;
const MIN_LOADING_MS = 1000;

function setGlobalLoading(on, text = 'Loading…', pct = null) {
  const gl = document.getElementById('globalLoading');
  const t = document.getElementById('loadingText');
  const b = document.getElementById('loadingBar');
  if (!gl || !t || !b) return;

  if (on) {
    if (gl.hidden) {
      gLoadingShownAt = Date.now();
    }
    gl.hidden = false;
    t.textContent = text;

    if (pct != null) {
      const clamped = Math.max(0, Math.min(100, pct));
      b.style.width = `${clamped}%`;
    }
    return;
  }

  // Delay hiding a bit so it's actually visible (prevents "never showed" when
  // operations complete extremely quickly).
  const elapsed = Date.now() - (gLoadingShownAt || Date.now());
  const wait = Math.max(0, MIN_LOADING_MS - elapsed);
  window.setTimeout(() => {
    gl.hidden = true;
  }, wait);
}

function renderMediaList(items) {
  const el = document.getElementById('mediaList');
  if (!el) return;

  el.innerHTML = '';
  gMedia = Array.isArray(items) ? items : [];

  resetPosterState();
  ensurePosterObserver();

  if (!items || items.length === 0) {
    const div = document.createElement('div');
    div.className = 'empty';
    div.textContent = 'No media discovered yet.';
    el.appendChild(div);
    return;
  }

  items.forEach((item, idx) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.tabIndex = 0;

    if (item.media_type === 'image') {
      const sk = document.createElement('div');
      sk.className = 'skel';
      card.appendChild(sk);

      const img = document.createElement('img');
      img.className = 'thumb';
      img.loading = 'lazy';
      img.src = item.url;
      img.alt = '';
      img.addEventListener('load', () => sk.remove());
      img.addEventListener('error', () => sk.remove());
      card.appendChild(img);

      card.addEventListener('click', () => openLightboxByIndex(idx));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') openLightboxByIndex(idx);
      });
    } else {
      const sk = document.createElement('div');
      sk.className = 'skel';
      card.appendChild(sk);
      // Video tile: lazy poster load only when near viewport.
      const img = document.createElement('img');
      img.className = 'thumb poster';
      img.alt = '';
      img.setAttribute('data-video-path', item.path || '');
      img.addEventListener('load', () => sk.remove());
      img.addEventListener('error', () => sk.remove());
      card.appendChild(img);

      const badge = document.createElement('div');
      badge.className = 'videoBadge';
      badge.textContent = 'VIDEO';
      card.appendChild(badge);

      if (item.path) gPosterObserver.observe(img);

      card.addEventListener('click', () => openLightboxByIndex(idx));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') openLightboxByIndex(idx);
      });
    }

    el.appendChild(card);
  });
}

let gMedia = [];
let gIndex = -1;
let gBridge = null;
let gPage = 0;
let gTotal = 0;
const PAGE_SIZE = 100;

// Lazy poster loading for videos
let gPosterObserver = null;
const gPosterRequested = new Set();

let gLightboxNativeVideo = false;

function openLightboxByIndex(idx) {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lightboxImg');
  const vid = document.getElementById('lightboxVideo');
  if (!lb || !img || !vid) return;

  // Stop native overlay ONLY if it was previously opened for a video.
  if (gLightboxNativeVideo && gBridge && gBridge.close_native_video) {
    gBridge.close_native_video(function () {});
  }
  gLightboxNativeVideo = false;

  if (!gMedia || gMedia.length === 0) return;
  if (idx < 0) idx = 0;
  if (idx >= gMedia.length) idx = gMedia.length - 1;

  gIndex = idx;

  const item = gMedia[gIndex];
  if (item.media_type === 'video') {
    // Open web lightbox chrome, but delegate actual video rendering to native overlay.
    // (QtWebEngine codec support is unreliable on Windows.)
    const lb = document.getElementById('lightbox');
    const imgEl = document.getElementById('lightboxImg');
    const vidEl = document.getElementById('lightboxVideo');
    if (lb) lb.hidden = false;
    if (imgEl) {
      imgEl.style.display = 'none';
      imgEl.src = '';
    }
    if (vidEl) {
      vidEl.style.display = 'none';
      vidEl.src = '';
    }
    document.body.style.overflow = 'hidden';

    if (gBridge && gBridge.open_native_video && item.path) {
      gLightboxNativeVideo = true;
      gBridge.get_video_duration_seconds(item.path, function (dur) {
        const seconds = Number(dur || 0);
        const short = seconds > 0 && seconds < 60;
        gBridge.open_native_video(item.path, short, short, short);
      });
    }
    return;
  } else {
    vid.pause();
    vid.style.display = 'none';
    vid.src = '';
    img.style.display = 'block';
    img.src = item.url;
  }

  lb.hidden = false;

  // prevent background scroll while open
  document.body.style.overflow = 'hidden';
}

let gClosingFromNative = false;

function closeLightbox() {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lightboxImg');
  const vid = document.getElementById('lightboxVideo');
  if (!lb || !img || !vid) return;
  lb.hidden = true;

  img.src = '';
  img.style.display = 'block';

  vid.pause();
  vid.src = '';
  vid.style.display = 'none';

  if (!gClosingFromNative && gBridge && gBridge.close_native_video) {
    gBridge.close_native_video(function () {});
  }

  gIndex = -1;
  document.body.style.overflow = '';
}

// Called from native when the native overlay closes.
window.__mmx_closeLightboxFromNative = function () {
  gClosingFromNative = true;
  try {
    closeLightbox();
  } finally {
    gClosingFromNative = false;
  }
};

function lightboxPrev() {
  if (gIndex <= 0) return;
  openLightboxByIndex(gIndex - 1);
}

function lightboxNext() {
  if (gMedia && gIndex >= 0 && gIndex < gMedia.length - 1) {
    openLightboxByIndex(gIndex + 1);
  }
}

function wireLightbox() {
  const backdrop = document.getElementById('lightboxBackdrop');
  const img = document.getElementById('lightboxImg');
  const vid = document.getElementById('lightboxVideo');

  // Click outside closes (most clicks should hit backdrop because content has pointer-events:none)
  if (backdrop) backdrop.addEventListener('click', closeLightbox);
  if (img) img.addEventListener('click', (e) => e.stopPropagation());
  if (vid) vid.addEventListener('click', (e) => e.stopPropagation());

  const btnPrev = document.getElementById('lbPrev');
  const btnNext = document.getElementById('lbNext');
  const btnClose = document.getElementById('lbClose');
  if (btnPrev) btnPrev.addEventListener('click', lightboxPrev);
  if (btnNext) btnNext.addEventListener('click', lightboxNext);
  if (btnClose) btnClose.addEventListener('click', closeLightbox);

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') lightboxPrev();
    if (e.key === 'ArrowRight') lightboxNext();
  });
}

function totalPages() {
  return Math.max(1, Math.ceil((gTotal || 0) / PAGE_SIZE));
}

function pagerPagesToShow() {
  const tp = totalPages();
  const cur = gPage + 1; // 1-based
  const set = new Set([1, tp, cur]);
  if (cur - 1 >= 1) set.add(cur - 1);
  if (cur + 1 <= tp) set.add(cur + 1);
  return Array.from(set).sort((a, b) => a - b);
}

function renderPager() {
  const tp = totalPages();
  const cur = gPage + 1;

  const pages = pagerPagesToShow();

  document.querySelectorAll('[data-pager]').forEach((root) => {
    const prev = root.querySelector('[data-prev]');
    const next = root.querySelector('[data-next]');
    const links = root.querySelector('[data-links]');

    if (prev) prev.disabled = gPage === 0;
    if (next) next.disabled = cur >= tp;

    if (!links) return;
    links.innerHTML = '';

    let last = 0;
    for (const p of pages) {
      if (last && p > last + 1) {
        const ell = document.createElement('span');
        ell.className = 'tb-ellipsis';
        ell.textContent = '…';
        links.appendChild(ell);
      }

      const btn = document.createElement('button');
      btn.className = 'tb-page';
      btn.textContent = String(p);
      if (p === cur) btn.setAttribute('aria-current', 'page');
      btn.addEventListener('click', () => {
        gPage = p - 1;
        refreshFromBridge(gBridge);
      });
      links.appendChild(btn);

      last = p;
    }
  });
}

function refreshFromBridge(bridge) {
  bridge.get_selected_folder(function (folder) {
    setSelectedFolder(folder);
    if (!folder) {
      gTotal = 0;
      setGlobalLoading(false);
      renderMediaList([]);
      renderPager();
      return;
    }

    setGlobalLoading(true, 'Scanning media…', 15);

    bridge.count_media(folder, function (count) {
      gTotal = count || 0;
      const tp = totalPages();
      if (gPage >= tp) gPage = tp - 1;

      setGlobalLoading(true, `Loading page ${gPage + 1} of ${tp}…`, 55);

      bridge.list_media(folder, PAGE_SIZE, gPage * PAGE_SIZE, function (items) {
        renderMediaList(items);
        renderPager();
        // Hide after containers are painted at least once.
        requestAnimationFrame(() => setGlobalLoading(false));
      });
    });
  });
}

function nextPage() {
  if (!gBridge) return;
  const tp = totalPages();
  gPage = Math.min(tp - 1, gPage + 1);
  refreshFromBridge(gBridge);
}

function prevPage() {
  if (!gBridge) return;
  gPage = Math.max(0, gPage - 1);
  refreshFromBridge(gBridge);
}

function wirePager() {
  document.querySelectorAll('[data-pager]').forEach((root) => {
    const prev = root.querySelector('[data-prev]');
    const next = root.querySelector('[data-next]');
    if (prev) prev.addEventListener('click', prevPage);
    if (next) next.addEventListener('click', nextPage);
  });
  renderPager();
}

function openSettings() {
  const m = document.getElementById('settingsModal');
  if (m) m.hidden = false;
}

function closeSettings() {
  const m = document.getElementById('settingsModal');
  if (m) m.hidden = true;
}

function wireSettings() {
  const openBtn = document.getElementById('openSettings');
  const closeBtn = document.getElementById('closeSettings');
  const reshuf = document.getElementById('reshuffle');
  const backdrop = document.getElementById('settingsBackdrop');
  const toggle = document.getElementById('toggleRandomize');

  if (openBtn) openBtn.addEventListener('click', openSettings);
  if (closeBtn) closeBtn.addEventListener('click', closeSettings);
  if (backdrop) backdrop.addEventListener('click', closeSettings);

  if (reshuf) {
    reshuf.addEventListener('click', () => {
      if (!gBridge || !gBridge.reshuffle_gallery) return;
      gBridge.reshuffle_gallery(function () {
        gPage = 0;
        refreshFromBridge(gBridge);
      });
    });
  }

  if (toggle) {
    toggle.addEventListener('change', () => {
      if (!gBridge || !gBridge.set_setting_bool) return;
      gBridge.set_setting_bool('gallery.randomize', !!toggle.checked, function () {
        gPage = 0;
        refreshFromBridge(gBridge);
      });
    });
  }
}

async function main() {
  wireLightbox();
  wirePager();
  wireSettings();

  // Show immediately on first paint (prevents "nothing then overlay" behavior)
  setGlobalLoading(true, 'Starting…', 10);
  setStatus('Loading bridge…');

  if (!window.qt || !window.qt.webChannelTransport) {
    setStatus('No Qt bridge (running in a normal browser?)');
    return;
  }

  // Expose a bridge object from Qt.
  new QWebChannel(window.qt.webChannelTransport, function (channel) {
    const bridge = channel.objects.bridge;
    if (!bridge) {
      setStatus('Bridge missing');
      return;
    }

    gBridge = bridge;

    bridge.get_tools_status(function (st) {
      const ff = st && st.ffmpeg ? 'ffmpeg✓' : 'ffmpeg×';
      const fp = st && st.ffprobe ? 'ffprobe✓' : 'ffprobe×';
      const td = st && st.thumb_dir ? st.thumb_dir : '';
      setStatus(`Ready (${ff}, ${fp})${td ? ' | thumbs: ' + td : ''}`);
      console.log('tools_status', st);
    });

    bridge.get_settings(function (s) {
      const t = document.getElementById('toggleRandomize');
      if (t) t.checked = !!(s && s['gallery.randomize']);
    });

    // Initial sync
    refreshFromBridge(bridge);

    // React to future changes
    if (bridge.selectedFolderChanged) {
      bridge.selectedFolderChanged.connect(function () {
        gPage = 0;
        refreshFromBridge(bridge);
      });
    }
  });
}

main();
