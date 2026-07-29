from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from .common import section_frame, value_text


class _DecisionCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WritePolicyDecisionCard")
        self.setStyleSheet("QFrame#WritePolicyDecisionCard { background: #eaf2ff; color: #17324f; border: 1px solid #8cadd0; border-radius: 7px; }")
        layout = QVBoxLayout(self)
        self.heading = QLabel("N/A"); self.heading.setStyleSheet("color: #17324f; font-size: 16px; font-weight: 800;")
        self.body = QLabel("No selected step"); self.body.setWordWrap(True); self.body.setTextInteractionFlags(self.body.textInteractionFlags())
        self.body.setStyleSheet("color: #17324f;")
        layout.addWidget(self.heading); layout.addWidget(self.body)

    def render(self, model):
        if model is None:
            self.heading.setText("N/A"); self.body.setText("No selected step"); return
        allocation = "Write-Allocate" if model.write_allocate else "No-Write-Allocate"
        dirty_event = "\nDIRTY EVICTION / WRITE-BACK" if model.victim_dirty and model.evicted_way is not None else ""
        self.heading.setText(f"{model.lane_label} — {model.result_label}")
        self.body.setText(
            f"Policy: {model.write_policy} / {allocation}\n"
            f"Decision: {model.decision_kind}{dirty_event}\n"
            f"Allocated: {value_text(model.allocated)} | Bypassed: {value_text(model.bypassed)}\n"
            f"Hit way: {value_text(model.hit_way)} | Fill way: {value_text(model.fill_way)} | Evicted way: {value_text(model.evicted_way)}\n"
            f"Victim tag: {value_text(model.victim_tag)} | Victim dirty: {value_text(model.victim_dirty)}\n"
            f"Dirty before → after: {value_text(model.line_dirty_before)} → {value_text(model.line_dirty_after)}\n"
            f"Step traffic (B): fill {model.traffic.block_fill_bytes}, immediate {model.traffic.immediate_store_bytes}, "
            f"bypass {model.traffic.bypass_write_bytes}, write-back {model.traffic.dirty_writeback_bytes}\n"
            f"Memory read/write/total (B): {model.traffic.memory_read_bytes} / {model.traffic.memory_write_bytes} / {model.traffic.total_lower_memory_bytes}\n"
            f"Reason: {model.classification_reason}\nRule path: {' → '.join(model.rule_path)}\n"
            f"Metadata consistent: {value_text(model.metadata_consistent)}"
        )
        self.setStyleSheet(
            "QFrame#WritePolicyDecisionCard { background: #ffe5e5; color: #681b1b; border: 2px solid #ba4b4b; border-radius: 7px; }"
            if not model.metadata_consistent else
            "QFrame#WritePolicyDecisionCard { background: #eaf2ff; color: #17324f; border: 1px solid #8cadd0; border-radius: 7px; }"
        )


class DecisionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        frame, layout = section_frame("Selected Historical Evidence: Four Lane Decisions")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(frame)
        grid = QGridLayout(); layout.addLayout(grid)
        self.cards = tuple(_DecisionCard() for _ in range(4))
        for index, card in enumerate(self.cards): grid.addWidget(card, index // 2, index % 2)

    def render(self, decisions):
        for index, card in enumerate(self.cards):
            card.render(decisions[index] if index < len(decisions) else None)


__all__ = ["DecisionPanel"]
