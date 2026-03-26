"""Settings dialog for theme, computation mode, etc."""

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setMinimumWidth(350)

        settings = QSettings()

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # 外観
        self._appearance_combo = QComboBox()
        self._appearance_combo.addItems(["システム (自動)", "ライト", "ダーク"])
        current = settings.value("appearance", "media")
        index_map = {"media": 0, "light": 1, "dark": 2}
        self._appearance_combo.setCurrentIndex(index_map.get(current, 0))
        form.addRow("外観:", self._appearance_combo)

        # チャートテーマ
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["g2", "vega"])
        current_theme = settings.value("theme_key", "g2")
        self._theme_combo.setCurrentText(current_theme)
        form.addRow("チャートテーマ:", self._theme_combo)

        # デフォルトタブ
        self._tab_combo = QComboBox()
        self._tab_combo.addItems(["可視化", "データ"])
        current_tab = settings.value("default_tab", "vis")
        tab_display_map = {"vis": "可視化", "data": "データ"}
        self._tab_combo.setCurrentText(tab_display_map.get(current_tab, "可視化"))
        form.addRow("デフォルトタブ:", self._tab_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        settings = QSettings()
        appearance_map = {0: "media", 1: "light", 2: "dark"}
        settings.setValue("appearance", appearance_map[self._appearance_combo.currentIndex()])
        settings.setValue("theme_key", self._theme_combo.currentText())
        tab_value_map = {"可視化": "vis", "データ": "data"}
        settings.setValue("default_tab", tab_value_map.get(self._tab_combo.currentText(), "vis"))
        super().accept()
