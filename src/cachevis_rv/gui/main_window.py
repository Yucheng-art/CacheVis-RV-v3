"""V3 platform shell coordinating sidebar, Home, and lazy lab pages."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QWidget,
)

from version import APP_DESCRIPTION, APP_NAME, APP_VERSION

from .home_page import HomePage
from .lab_registry import AVAILABLE, get_lab
from .navigation_sidebar import NavigationSidebar
from .theme import PLATFORM_STYLESHEET


ABOUT_TITLE = "About CacheVis-RV"
ABOUT_TEXT = (
    f"{APP_NAME}\n"
    f"Version: {APP_VERSION}\n\n"
    f"{APP_DESCRIPTION}\n\n"
    "Current support:\n"
    "- Single experiment GUI\n"
    "- GUI parameter comparison experiments\n"
    "- CLI experiments\n"
    "- CSV/Markdown export\n\n"
    "Not yet supported:\n"
    "- EXE packaging\n"
    "- Formal copyright application material generation"
)


class CacheVisMainWindow(QMainWindow):
    """Lightweight platform shell with cached, registry-created lab pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 680)
        self._page_cache: dict[str, QWidget] = {}
        self._current_page_id = "home"
        self._build_ui()
        self._build_menu()
        self.setStyleSheet(PLATFORM_STYLESHEET)
        self.statusBar().showMessage(
            "Home | Choose a learning lab or classic experiment tool."
        )

    def _build_ui(self) -> None:
        shell = QWidget()
        shell.setObjectName("PlatformShell")
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = NavigationSidebar()
        self.sidebar.navigation_requested.connect(self.navigate_to)
        layout.addWidget(self.sidebar, 0)

        self.page_stack = QStackedWidget()
        self.home_page = HomePage()
        self.home_page.navigation_requested.connect(self.navigate_to)
        self.page_stack.addWidget(self.home_page)
        self._page_cache["home"] = self.home_page
        layout.addWidget(self.page_stack, 1)

        self.setCentralWidget(shell)
        self.page_stack.setCurrentWidget(self.home_page)
        self.sidebar.set_current("home")

    def _build_menu(self) -> None:
        help_menu = self.menuBar().addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def navigate_to(self, page_id: str) -> bool:
        """Navigate to Home or lazily create and reuse an available lab page."""
        if page_id == "home":
            self._show_cached_page("home", "Home")
            return True

        lab = get_lab(page_id)
        if lab is None:
            self.statusBar().showMessage(f"Unknown lab: {page_id}")
            return False
        if lab.status != AVAILABLE or lab.factory is None:
            self.statusBar().showMessage(f"{lab.title} | Coming Soon")
            return False

        if page_id not in self._page_cache:
            page = lab.factory()
            if not isinstance(page, QWidget):
                raise TypeError(f"factory for {page_id} did not return a QWidget")
            self._page_cache[page_id] = page
            self.page_stack.addWidget(page)

        self._show_cached_page(page_id, lab.title)
        return True

    def _show_cached_page(self, page_id: str, title: str) -> None:
        page = self._page_cache[page_id]
        self.page_stack.setCurrentWidget(page)
        self.sidebar.set_current(page_id)
        self._current_page_id = page_id
        self.statusBar().showMessage(f"{title} | Ready")

    def page_for(self, page_id: str) -> QWidget | None:
        """Return an already-created page without triggering construction."""
        return self._page_cache.get(page_id)

    @property
    def current_page_id(self) -> str:
        return self._current_page_id

    def show_about_dialog(self) -> None:
        create_about_message_box(self).exec()


def create_about_message_box(parent: QWidget | None = None) -> QMessageBox:
    """Create the platform About dialog."""
    box = QMessageBox(parent)
    box.setWindowTitle(ABOUT_TITLE)
    box.setText(ABOUT_TEXT)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return box


__all__ = ["CacheVisMainWindow", "create_about_message_box"]
