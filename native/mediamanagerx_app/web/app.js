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

    if (item.media_type === 'image') {
      const img = document.createElement('img');
      img.className = 'thumb';
      img.loading = 'lazy';
      img.src = item.url;
      img.alt = item.path;
      card.appendChild(img);
    } else {
      const ph = document.createElement('div');
      ph.className = 'thumb placeholder';
      ph.textContent = 'VIDEO';
      card.appendChild(ph);
    }

    const cap = document.createElement('div');
    cap.className = 'caption';
    cap.textContent = item.path;
    card.appendChild(cap);

    el.appendChild(card);
  }
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
