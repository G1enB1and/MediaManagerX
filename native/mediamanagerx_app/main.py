from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal, Slot, QUrl
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
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView


class Bridge(QObject):
    selectedFolderChanged = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._selected_folder: str = ""

    def set_selected_folder(self, folder: str) -> None:
        folder = folder or ""
        if folder == self._selected_folder:
            return
        self._selected_folder = folder
        self.selectedFolderChanged.emit(self._selected_folder)

    @Slot(result=str)
    def get_selected_folder(self) -> str:
        return self._selected_folder

    @Slot(str, int, result=list)
    def list_media(self, folder: str, limit: int = 100) -> list[str]:
        """Return a simple list of media file paths under folder.

        This is intentionally a tiny first bridge method so the Web UI can
        show *something real* immediately.
        """

        try:
            root = Path(folder)
            if not root.exists() or not root.is_dir():
                return []

            exts = {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".gif",
                ".bmp",
                ".mp4",
                ".webm",
                ".mov",
                ".mkv",
            }

            out: list[str] = []
            for p in root.rglob("*"):
                if len(out) >= int(limit):
                    break
                if p.is_file() and p.suffix.lower() in exts:
                    out.append(str(p))
            return out
        except Exception:
            # Don't crash the bridge; the UI can display empty state.
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

        # Left: folder/scope placeholder
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.addWidget(QLabel("Folder scope (placeholder)"))
        self.scope_label = QLabel("No folder selected")
        self.scope_label.setWordWrap(True)
        left_layout.addWidget(self.scope_label)
        left_layout.addStretch(1)

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

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose a media folder")
        if folder:
            folder_path = str(Path(folder))
            self.scope_label.setText(folder_path)
            self.bridge.set_selected_folder(folder_path)

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
