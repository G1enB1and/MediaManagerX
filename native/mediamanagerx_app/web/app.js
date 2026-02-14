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
  if (!items || items.length === 0) {
    const div = document.createElement('div');
    div.className = 'empty';
    div.textContent = 'No media discovered yet.';
    el.appendChild(div);
    return;
  }

  for (const item of items) {
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

      card.addEventListener('click', () => openLightbox(item.url));
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') openLightbox(item.url);
      });
    } else {
      const ph = document.createElement('div');
      ph.className = 'thumb placeholder';
      ph.textContent = 'VIDEO';
      card.appendChild(ph);
    }

    el.appendChild(card);
  }
}

function openLightbox(url) {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lightboxImg');
  if (!lb || !img) return;
  img.src = url;
  lb.hidden = false;
}

function closeLightbox() {
  const lb = document.getElementById('lightbox');
  const img = document.getElementById('lightboxImg');
  if (!lb || !img) return;
  lb.hidden = true;
  img.src = '';
}

function wireLightbox() {
  const backdrop = document.getElementById('lightboxBackdrop');
  if (backdrop) backdrop.addEventListener('click', closeLightbox);
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLightbox();
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
