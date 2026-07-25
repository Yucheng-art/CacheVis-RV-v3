"""PySide6 widget for drawing a colored Tag / Index / Offset bit bar."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..address_bits import AddressBitSegment, split_address_bit_segments


SEGMENT_STYLES = {
    "Tag": ("#ffd6d6", "#8a1f1f"),
    "Index": ("#d9f7d9", "#1f6b2a"),
    "Offset": ("#d7e8ff", "#1f4f8f"),
}

SEGMENT_TEXT_COLORS = {
    "Tag": "#6b1f1f",
    "Index": "#14532d",
    "Offset": "#173f73",
}


class AddressBitBarWidget(QWidget):
    """Responsive colored bit bar for Tag / Index / Offset display."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._segment_frames: dict[str, QFrame] = {}
        self._segment_labels: dict[str, QLabel] = {}
        self._bar_layout: QHBoxLayout | None = None
        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.scale_label = QLabel("MSB on left | LSB on right")
        self.scale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.scale_label)

        self._bar_layout = QHBoxLayout()
        self._bar_layout.setSpacing(4)
        for name in ("Tag", "Index", "Offset"):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setMinimumHeight(92)
            frame.setMinimumWidth(110)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(8, 6, 8, 6)

            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setStyleSheet("font-family: Consolas, monospace;")
            frame_layout.addWidget(label)

            self._segment_frames[name] = frame
            self._segment_labels[name] = label
            self._bar_layout.addWidget(frame, 1)
        layout.addLayout(self._bar_layout)

        self.range_label = QLabel("Tag: - | Index: - | Offset: -")
        self.range_label.setWordWrap(True)
        self.range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.range_label)

    def clear(self) -> None:
        """Reset the bar to a placeholder state."""
        self.scale_label.setText("MSB on left | LSB on right")
        self.range_label.setText("Tag: - | Index: - | Offset: -")
        for name in ("Tag", "Index", "Offset"):
            self._set_segment_display(
                AddressBitSegment(name, "", 0, 0, None, None, f"{name}: none (0 bits)")
            )
        self._set_stretches([1, 1, 1])

    def set_address(
        self,
        *,
        address_binary: str,
        tag_bits: int,
        index_bits: int,
        offset_bits: int,
        tag: int,
        index: int,
        offset: int,
    ) -> None:
        """Update the bar from the current address split."""
        segments = split_address_bit_segments(
            address_binary,
            tag_bits,
            index_bits,
            offset_bits,
            tag,
            index,
            offset,
        )
        address_bits = len(address_binary)
        self.scale_label.setText(
            f"bit {address_bits - 1} (MSB) on left ... bit 0 (LSB) on right | "
            f"address_bits = {address_bits}"
        )
        self.range_label.setText(" | ".join(segment.range_label for segment in segments))
        for segment in segments:
            self._set_segment_display(segment)
        self._set_stretches([max(segment.bit_count, 1) for segment in segments])

    def _set_segment_display(self, segment: AddressBitSegment) -> None:
        label = self._segment_labels[segment.name]
        bit_text = segment.bits if segment.bits else "none"
        label.setText(
            f"{segment.name}\n"
            f"{bit_text}\n"
            f"{segment.bit_count} bit(s)\n"
            f"value = {segment.value}"
        )

        bg, border = SEGMENT_STYLES[segment.name]
        text = SEGMENT_TEXT_COLORS[segment.name]
        self._segment_frames[segment.name].setStyleSheet(
            "QFrame {"
            f"background-color: {bg};"
            f"border: 2px solid {border};"
            "border-radius: 6px;"
            f"color: {text};"
            "}"
        )

    def _set_stretches(self, stretches: list[int]) -> None:
        if self._bar_layout is None:
            return
        for index, stretch in enumerate(stretches):
            self._bar_layout.setStretch(index, stretch)
