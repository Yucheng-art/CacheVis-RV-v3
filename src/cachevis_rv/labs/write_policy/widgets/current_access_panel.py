from PySide6.QtWidgets import QLabel, QGridLayout, QVBoxLayout, QWidget

from .common import section_frame, value_text


class CurrentAccessPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Current Access and Run Position")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        grid = QGridLayout(); layout.addLayout(grid)
        self.values = {}
        fields = ("Total Steps", "Next Step", "Latest Step", "Selected Step", "Complete", "Selected Is Latest", "Access", "Address", "Block", "Set", "Tag")
        for index, name in enumerate(fields):
            grid.addWidget(QLabel(name), index // 4 * 2, index % 4)
            label = QLabel("N/A"); label.setObjectName("WritePolicyPosition" + name.replace(" ", ""))
            grid.addWidget(label, index // 4 * 2 + 1, index % 4)
            self.values[name] = label
        self.history_notice = QLabel("Viewing historical evidence; cache and statistics remain at the latest run state.")
        self.history_notice.setWordWrap(True)
        self.history_notice.setStyleSheet("background: #fff2cc; color: #5b4100; padding: 8px; border: 1px solid #c99a13;")
        layout.addWidget(self.history_notice)

    def render(self, state):
        if not state.has_experiment:
            for label in self.values.values(): label.setText("N/A")
            self.history_notice.hide(); return
        selected = state.selected_step
        data = {
            "Total Steps": state.total_steps,
            "Next Step": state.next_step_index,
            "Latest Step": state.latest_step_index,
            "Selected Step": state.selected_step_index,
            "Complete": state.is_complete,
            "Selected Is Latest": state.selected_is_latest,
            "Access": None if selected is None else selected.access.kind.value.upper(),
            "Address": None if selected is None else f"{selected.access.address} / {selected.address_hex}",
            "Block": None if selected is None else selected.block_address,
            "Set": None if selected is None else selected.set_index,
            "Tag": None if selected is None else selected.tag,
        }
        for name, value in data.items(): self.values[name].setText(value_text(value))
        self.history_notice.setVisible(selected is not None and not state.selected_is_latest)


__all__ = ["CurrentAccessPanel"]
