/* global QWebChannel */

function setStatus(text) {
  const el = document.getElementById('status');
  if (el) el.textContent = text;
}

function setSelectedFolder(text) {
  const el = document.getElementById('selectedFolder');
  if (el) el.textContent = text || '(none)';
}

function renderMediaList(items) {
  const el = document.getElementById('mediaList');
  if (!el) return;

  el.innerHTML = '';
  gMedia = Array.isArray(items) ? items : [];

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
      const img = document.createElement('img');
      img.className = 'thumb';
      img.loading = 'lazy';
      img.src = item.url;
      img.alt = '';
      card.appendChild(img);

      card.addEventListener('click', () => openLightboxByIndex(idx));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') openLightboxByIndex(idx);
      });
    } else {
      const ph = document.createElement('div');
      ph.className = 'thumb placeholder';
      ph.textContent = 'VIDEO';
      card.appendChild(ph);

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

function openLightboxByIndex(idx) {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lightboxImg');
  const vid = document.getElementById('lightboxVideo');
  if (!lb || !img || !vid) return;

  if (!gMedia || gMedia.length === 0) return;
  if (idx < 0) idx = 0;
  if (idx >= gMedia.length) idx = gMedia.length - 1;

  gIndex = idx;

  const item = gMedia[gIndex];
  if (item.media_type === 'video') {
    img.style.display = 'none';
    img.src = '';
    vid.style.display = 'block';
    vid.src = item.url;
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

  gIndex = -1;
  document.body.style.overflow = '';
}

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

function refreshFromBridge(bridge) {
  bridge.get_selected_folder(function (folder) {
    setSelectedFolder(folder);
    if (!folder) {
      renderMediaList([]);
      return;
    }
    bridge.list_media(folder, 100, function (items) {
      renderMediaList(items);
    });
  });
}

async function main() {
  wireLightbox();
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

    // Initial sync
    refreshFromBridge(bridge);
    setStatus('Ready');

    // React to future changes
    if (bridge.selectedFolderChanged) {
      bridge.selectedFolderChanged.connect(function () {
        refreshFromBridge(bridge);
      });
    }
  });
}

main();
