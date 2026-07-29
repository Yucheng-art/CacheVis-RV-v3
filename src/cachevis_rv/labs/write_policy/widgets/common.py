"""Small rendering helpers shared by Write Policy GUI panels."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


def value_text(value) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def section_frame(title: str):
    frame = QFrame()
    frame.setObjectName("WritePolicySection")
    frame.setStyleSheet(
        "QFrame#WritePolicySection { background: #111c2e; border: 1px solid #2b3d55; "
        "border-radius: 8px; }"
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(9)
    heading = QLabel(title)
    heading.setStyleSheet("font-size: 18px; font-weight: 800; color: #eef4ff;")
    layout.addWidget(heading)
    return frame, layout


__all__ = ["section_frame", "value_text"]
