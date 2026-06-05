from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
import src.gui.theme as theme


class DonutChart(QWidget):
    """Circular ring chart showing UP / DOWN / UNKNOWN proportions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(76, 76)
        self._up = 0
        self._down = 0
        self._unknown = 0

    def update_data(self, up: int, down: int, unknown: int):
        self._up = up
        self._down = down
        self._unknown = unknown
        self.update()

    def paintEvent(self, _event):
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        ring = 11
        pad = 6
        rect = QRectF(pad, pad, w - pad * 2, h - pad * 2)

        total = self._up + self._down + self._unknown

        if total == 0:
            pen = QPen(QColor(t.border), ring, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.FlatCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(rect)
        else:
            angle = 90 * 16  # 12 o'clock

            def _seg(count: int, color: str):
                nonlocal angle
                if count == 0:
                    return
                span = int(-round(count / total * 360 * 16))
                pen = QPen(QColor(color), ring, Qt.PenStyle.SolidLine,
                           Qt.PenCapStyle.FlatCap)
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawArc(rect, angle, span)
                angle += span

            _seg(self._up, t.hist_up_fg)
            _seg(self._down, t.hist_down_fg)
            _seg(self._unknown, t.hist_unknown_fg)

        # Centre label
        if total > 0:
            pct = int(100 * self._up / total)
            text = f"{pct}%"
            if pct >= 90:
                color = t.hist_up_fg
            elif pct < 50:
                color = t.hist_down_fg
            else:
                color = t.chart_axis
        else:
            text = "—"
            color = t.text_muted

        p.setPen(QColor(color))
        p.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        p.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, text)


class StatCard(QFrame):
    """Metric card: big coloured value + muted label."""

    def __init__(self, label: str, value_color: str, parent=None):
        super().__init__(parent)
        self._value_color = value_color
        self.setObjectName("stat_card")
        self.setFixedHeight(68)
        self.setMinimumWidth(110)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(2)

        self._val = QLabel("—")
        self._val.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self._val.setStyleSheet(
            f"color: {value_color}; background: transparent; border: none;"
        )

        self._lbl = QLabel(label)
        self._lbl.setFont(QFont("Segoe UI", 9))

        lay.addWidget(self._val)
        lay.addWidget(self._lbl)

    def set_value(self, v: str):
        self._val.setText(v)

    def refresh_theme(self):
        t = theme.current()
        self._lbl.setStyleSheet(
            f"color: {t.text_muted}; background: transparent; border: none;"
        )


class StatusSummary(QWidget):
    """Horizontal summary strip: donut chart + 4 stat cards."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("status_summary")
        self.setFixedHeight(84)

        t = theme.current()

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        self._donut = DonutChart()
        lay.addWidget(self._donut, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addSpacing(6)

        self._c_total   = StatCard("Total",       t.text)
        self._c_up      = StatCard("Online",      t.hist_up_fg)
        self._c_down    = StatCard("Offline",     t.hist_down_fg)
        self._c_latency = StatCard("Avg latency", t.accent)

        for card in (self._c_total, self._c_up, self._c_down, self._c_latency):
            lay.addWidget(card)

        lay.addStretch()
        self.refresh_theme()

    def update_stats(self, total: int, up: int, down: int, unknown: int,
                     avg_ms: str):
        self._donut.update_data(up, down, unknown)
        self._c_total.set_value(str(total))
        self._c_up.set_value(str(up))
        self._c_down.set_value(str(down))
        self._c_latency.set_value(avg_ms)

    def refresh_theme(self):
        t = theme.current()
        self.setStyleSheet(f"""
            QWidget#status_summary {{
                background-color: {t.surface};
                border-bottom: 1px solid {t.border};
            }}
            QFrame#stat_card {{
                background-color: {t.card_bg};
                border: 1px solid {t.border};
                border-radius: 10px;
            }}
        """)
        for card in (self._c_total, self._c_up, self._c_down, self._c_latency):
            card.refresh_theme()
        self._donut.update()
