"""PySide6 main-window shell for CacheVis-RV."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from cachevis_rv.labs.compare_experiment import CompareExperimentWidget
from cachevis_rv.labs.single_experiment import (
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    SingleExperimentWidget,
)
from version import APP_DESCRIPTION
from visualizer_widget import AddressVisualizerWidget


ABOUT_TITLE = "About CacheVis-RV"
ABOUT_TEXT = (
    f"{SOFTWARE_NAME}\n"
    f"Version: {SOFTWARE_VERSION}\n\n"
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
    """Top-level window that assembles the three existing lab pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{SOFTWARE_NAME} {SOFTWARE_VERSION}")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 680)
        self._build_ui()
        self._build_menu()
        self.statusBar().showMessage("Ready. Choose a tab and run an experiment.")

    def _build_ui(self) -> None:
        tabs = QTabWidget()
        tabs.addTab(AddressVisualizerWidget(), "Address Visualizer")
        tabs.addTab(SingleExperimentWidget(), "Single Experiment")
        tabs.addTab(CompareExperimentWidget(), "Compare Experiment")
        self.setCentralWidget(tabs)

    def _build_menu(self) -> None:
        help_menu = self.menuBar().addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self) -> None:
        """Show basic software information."""
        create_about_message_box(self).exec()


def create_about_message_box(parent: QWidget | None = None) -> QMessageBox:
    """Create the About dialog so tools can capture the same GUI content."""
    box = QMessageBox(parent)
    box.setWindowTitle(ABOUT_TITLE)
    box.setText(ABOUT_TEXT)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    return box


__all__ = ["CacheVisMainWindow", "create_about_message_box"]
