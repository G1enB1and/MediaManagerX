from __future__ import annotations

import sys
import hashlib
import subprocess
from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal, Slot, QUrl, QDir
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QWidget,
    QVBoxLayout,
    QTreeView,
    QFileSystemModel,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView


class Bridge(QObject):
    selectedFolderChanged = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._selected_folder: str = ""
        self._media_cache: dict[str, list[Path]] = {}
        self._thumb_dir = Path("data") / "thumbs"
        self._thumb_dir.mkdir(parents=True, exist_ok=True)

    def _thumb_key(self, path: Path) -> str:
        # Stable across runs; normalize separators + lowercase for Windows.
        s = str(path).replace("\\", "/").lower().encode("utf-8")
        return hashlib.sha1(s).hexdigest()

    def _video_poster_path(self, video_path: Path) -> Path:
        return self._thumb_dir / f"{self._thumb_key(video_path)}.jpg"

    def _ensure_video_poster(self, video_path: Path) -> Path | None:
        """Generate a poster jpg for a video using ffmpeg (if missing)."""

        out = self._video_poster_path(video_path)
        if out.exists():
            return out

        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            # Grab an early frame; scale down for gallery thumbnails.
            cmd = [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                "0",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-vf",
                "scale='min(640,iw)':-2",
                "-q:v",
                "4",
                str(out),
            ]
            subprocess.run(cmd, check=True)
            if out.exists():
                return out
            return None
        except Exception:
            return None

    def set_selected_folder(self, folder: str) -> None:
        folder = folder or ""
        if folder == self._selected_folder:
            return
        self._selected_folder = folder
        # Simple cache invalidation: folder change => new scan.
        self._media_cache.pop(folder, None)
        self.selectedFolderChanged.emit(self._selected_folder)

    @Slot(result=str)
    def get_selected_folder(self) -> str:
        return self._selected_folder

    def _scan_media_paths(self, folder: str) -> list[Path]:
        cached = self._media_cache.get(folder)
        if cached is not None:
            return cached

        root = Path(folder)
        if not root.exists() or not root.is_dir():
            self._media_cache[folder] = []
            return []

        image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
        video_exts = {".mp4", ".webm", ".mov", ".mkv"}
        exts = image_exts | video_exts

        candidates: list[Path] = []
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in exts:
                candidates.append(p)

        candidates.sort(key=lambda p: str(p).lower())
        self._media_cache[folder] = candidates
        return candidates

    @Slot(str, result=int)
    def count_media(self, folder: str) -> int:
        """Return total number of discoverable media items under folder."""

        try:
            return len(self._scan_media_paths(folder))
        except Exception:
            return 0

    @Slot(str, result=str)
    def get_video_poster(self, video_path: str) -> str:
        """Return a file:// URL for a cached/generated poster image for a video."""

        try:
            p = Path(video_path)
            out = self._ensure_video_poster(p)
            if not out:
                return ""
            return QUrl.fromLocalFile(str(out)).toString()
        except Exception:
            return ""

    @Slot(str, int, int, result=list)
    def list_media(self, folder: str, limit: int = 100, offset: int = 0) -> list[dict]:
        """Return a list of media entries under folder.

        Each entry is a dict:
          {"path": <fs-path>, "url": <file://...>, "media_type": "image"|"video"}
        """

        try:
            image_exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

            candidates = self._scan_media_paths(folder)
            start = max(0, int(offset))
            end = start + max(0, int(limit))
            page = candidates[start:end]

            out: list[dict] = []
            for p in page:
                media_type = "image" if p.suffix.lower() in image_exts else "video"
                out.append(
                    {
                        "path": str(p),
                        "url": QUrl.fromLocalFile(str(p)).toString(),
                        "media_type": media_type,
                    }
                )

            return out
        except Exception:
            return []


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MediaManagerX")
        self.resize(1200, 800)

        self.bridge = Bridge()

        self._build_menu()
        self._build_layout()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")

        pick_action = QAction("Choose &Folder…", self)
        pick_action.triggered.connect(self.choose_folder)
        file_menu.addAction(pick_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

    def _build_layout(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: folder tree (native) — functional first, styling later
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 8, 8, 8)

        left_layout.addWidget(QLabel("Folders"))

        default_root = Path("C:/Pictures")
        if not default_root.exists():
            default_root = Path.home() / "Pictures"
        if not default_root.exists():
            default_root = Path.home()

        self.fs_model = QFileSystemModel(self)
        self.fs_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        self.fs_model.setRootPath(str(default_root))

        self.tree = QTreeView()
        self.tree.setModel(self.fs_model)
        self.tree.setRootIndex(self.fs_model.index(str(default_root)))
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(14)
        self.tree.setExpandsOnDoubleClick(True)

        # Hide columns: keep only name
        for col in range(1, self.fs_model.columnCount()):
            self.tree.hideColumn(col)

        self.tree.selectionModel().selectionChanged.connect(self._on_tree_selection)

        left_layout.addWidget(self.tree, 1)

        self._set_selected_folder(str(default_root))

        # Right: embedded WebEngine UI scaffold
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.web = QWebEngineView()
        right_layout.addWidget(self.web)

        channel = QWebChannel(self.web.page())
        channel.registerObject("bridge", self.bridge)
        self.web.page().setWebChannel(channel)

        index_path = Path(__file__).with_name("web") / "index.html"
        self.web.setUrl(QUrl.fromLocalFile(str(index_path.resolve())))

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        self.setCentralWidget(splitter)

    def _set_selected_folder(self, folder_path: str) -> None:
        self.bridge.set_selected_folder(folder_path)

    def _on_tree_selection(self, *_args) -> None:
        idx = self.tree.currentIndex()
        if not idx.isValid():
            return
        path = self.fs_model.filePath(idx)
        if path:
            self._set_selected_folder(path)

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose a media folder")
        if folder:
            folder_path = str(Path(folder))
            # Update the tree root and select the chosen folder.
            self.tree.setRootIndex(self.fs_model.index(folder_path))
            self.tree.setCurrentIndex(self.fs_model.index(folder_path))
            self._set_selected_folder(folder_path)

    def about(self) -> None:
        QMessageBox.information(
            self,
            "About MediaManagerX",
            "MediaManagerX\n\nWindows native app (PySide6) — UI shell in progress.",
        )


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
