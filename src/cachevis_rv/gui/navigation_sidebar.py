"""Stable left navigation for the V3 platform shell."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .lab_registry import get_available_labs
from .theme import SIDEBAR_WIDTH


class NavigationSidebar(QWidget):
    """Emit lab identifiers without constructing any lab page."""

    navigation_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("NavigationSidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self._buttons: dict[str, QPushButton] = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._build_ui()
        self.set_current("home")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 18)
        layout.setSpacing(5)

        brand = QLabel("CACHEVIS / RV V3")
        brand.setStyleSheet("font-size: 17px; font-weight: 800; padding: 4px 8px 16px 8px;")
        layout.addWidget(brand)

        self._add_navigation_button(layout, "home", "⌂  Home")
        available = get_available_labs()
        for category in ("Learn", "Classic Tools"):
            heading = QLabel(category.upper())
            heading.setProperty("role", "section")
            layout.addWidget(heading)
            for lab in available:
                if lab.category == category:
                    self._add_navigation_button(
                        layout,
                        lab.lab_id,
                        f"›  {lab.short_title}",
                    )
        layout.addStretch(1)

        footer = QLabel("Interactive Cache Learning Platform")
        footer.setWordWrap(True)
        footer.setProperty("role", "section")
        layout.addWidget(footer)

    def _add_navigation_button(
        self,
        layout: QVBoxLayout,
        lab_id: str,
        text: str,
    ) -> None:
        button = QPushButton(text)
        button.setCheckable(True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(
            lambda _checked=False, target=lab_id: self._request_navigation(target)
        )
        self._button_group.addButton(button)
        self._buttons[lab_id] = button
        layout.addWidget(button)

    def _request_navigation(self, lab_id: str) -> None:
        self.set_current(lab_id)
        self.navigation_requested.emit(lab_id)

    def set_current(self, lab_id: str) -> None:
        """Synchronize the selected navigation button."""
        button = self._buttons.get(lab_id)
        if button is not None:
            button.setChecked(True)

    @property
    def current_lab_id(self) -> str | None:
        """Return the currently checked navigation identifier."""
        for lab_id, button in self._buttons.items():
            if button.isChecked():
                return lab_id
        return None


__all__ = ["NavigationSidebar"]
