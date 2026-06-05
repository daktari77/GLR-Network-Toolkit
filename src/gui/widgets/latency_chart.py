from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath
from src.models import ProbeResult, HostStatus
import src.gui.theme as theme

_PAD = {"top": 24, "right": 12, "bottom": 28, "left": 46}
_MAX_POINTS = 500


class LatencyChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[tuple[float | None, bool]] = []  # (latency_ms, is_alive)
        self._host = ""
        self.setMinimumWidth(180)
        self.setMinimumHeight(100)

    def set_data(self, host: str, results: list[ProbeResult]):
        self._host = host
        self._data = [
            (r.latency_ms, r.status == HostStatus.UP)
            for r in results
        ]
        if len(self._data) > _MAX_POINTS:
            self._data = self._data[-_MAX_POINTS:]
        self.update()

    def append_point(self, result: ProbeResult):
        if result.host != self._host:
            return
        self._data.append((result.latency_ms, result.status == HostStatus.UP))
        if len(self._data) > _MAX_POINTS:
            self._data.pop(0)
        self.update()

    def clear(self):
        self._data.clear()
        self._host = ""
        self.update()

    def paintEvent(self, _event):
        t = theme.current()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        p.fillRect(0, 0, w, h, QColor(t.chart_bg))

        cx = _PAD["left"]
        cy = _PAD["top"]
        cw = w - _PAD["left"] - _PAD["right"]
        ch = h - _PAD["top"] - _PAD["bottom"]

        if not self._data or cw < 10 or ch < 10:
            p.setPen(QColor(t.chart_axis))
            p.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter,
                       "Select a host to view the latency chart")
            return

        valid_lats = [lat for lat, up in self._data if lat is not None and up]
        max_lat = (max(valid_lats) * 1.15) if valid_lats else 100.0
        max_lat = max(max_lat, 1.0)

        # Grid + Y labels
        grid_pen = QPen(QColor(t.chart_grid), 1)
        axis_pen = QPen(QColor(t.chart_axis), 1)
        p.setFont(QFont("Segoe UI", 8))

        for i in range(5):
            frac = i / 4
            gy = int(cy + ch - frac * ch)
            p.setPen(grid_pen)
            p.drawLine(cx, gy, cx + cw, gy)
            p.setPen(axis_pen)
            label = f"{frac * max_lat:.0f}"
            p.drawText(0, gy - 9, _PAD["left"] - 4, 18,
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                       label)

        # X axis line
        p.setPen(axis_pen)
        p.drawLine(cx, cy + ch, cx + cw, cy + ch)
        p.drawLine(cx, cy, cx, cy + ch)

        # Build point list
        n = len(self._data)

        def _px(i: int) -> float:
            return cx + (i / (n - 1)) * cw if n > 1 else cx + cw / 2

        def _py(lat: float | None) -> float:
            if lat is None:
                return cy + ch
            return cy + ch - min(lat / max_lat, 1.0) * ch

        # Draw UP line as path
        path = QPainterPath()
        in_path = False
        for i, (lat, up) in enumerate(self._data):
            if up and lat is not None:
                px, py = _px(i), _py(lat)
                if not in_path:
                    path.moveTo(px, py)
                    in_path = True
                else:
                    path.lineTo(px, py)
            else:
                in_path = False

        p.setPen(QPen(QColor(t.chart_line), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        # Draw DOWN dots
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(t.chart_dot))
        for i, (lat, up) in enumerate(self._data):
            if not up:
                px = int(_px(i))
                py = int(cy + ch - 4)
                p.drawEllipse(px - 3, py - 3, 6, 6)

        # UP-but-no-latency: small tick at baseline
        p.setPen(QPen(QColor(t.chart_line), 1))
        for i, (lat, up) in enumerate(self._data):
            if up and lat is None:
                px = int(_px(i))
                p.drawLine(px, cy + ch, px, cy + ch - 5)

        # Title
        p.setPen(QColor(t.chart_title))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(cx, 2, cw, _PAD["top"] - 2,
                   Qt.AlignmentFlag.AlignCenter,
                   f"{self._host} - latency ms ({n} samples)")

        # "ms" unit label
        p.setPen(QColor(t.chart_axis))
        p.drawText(0, cy, _PAD["left"] - 4, 14,
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                   "ms")
