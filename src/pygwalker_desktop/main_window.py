"""Main application window."""

from pathlib import Path
from typing import Optional

import pandas as pd
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QLabel,
)

from .data.loader import FILTER_STRING, load_file
from .server.bridge import ServerBridge
from .web_view import PygWalkerWebView


_MAX_RECENT = 10


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyGWalker Desktop")
        self.resize(1280, 800)

        self._server: Optional[ServerBridge] = None
        self._current_df: Optional[pd.DataFrame] = None
        self._current_file: Optional[str] = None
        self._appearance = "media"
        self._theme_key = "g2"

        # Central widget
        self._web_view = PygWalkerWebView(self)
        self.setCentralWidget(self._web_view)

        # Status bar
        self._status_label = QLabel("ファイル未読み込み")
        self.statusBar().addPermanentWidget(self._status_label)

        self._build_menus()
        self._build_toolbar()
        self._restore_geometry()

    # ── Menus ──

    def _build_menus(self):
        menu_bar = self.menuBar()

        # ファイルメニュー
        file_menu = menu_bar.addMenu("ファイル(&F)")

        open_action = QAction("開く(&O)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        self._recent_menu = file_menu.addMenu("最近開いたファイル(&R)")
        self._update_recent_menu()

        file_menu.addSeparator()

        export_spec = QAction("設定をエクスポート(&E)...", self)
        export_spec.triggered.connect(self._export_spec)
        file_menu.addAction(export_spec)

        import_spec = QAction("設定をインポート(&I)...", self)
        import_spec.triggered.connect(self._import_spec)
        file_menu.addAction(import_spec)

        file_menu.addSeparator()

        quit_action = QAction("終了(&Q)", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # 表示メニュー
        view_menu = menu_bar.addMenu("表示(&V)")

        self._theme_actions = {}
        for label, value in [("ライト", "light"), ("ダーク", "dark"), ("システム", "media")]:
            action = QAction(label, self, checkable=True)
            action.setChecked(value == self._appearance)
            action.triggered.connect(lambda checked, v=value: self._set_appearance(v))
            view_menu.addAction(action)
            self._theme_actions[value] = action

        view_menu.addSeparator()

        zoom_in = QAction("拡大(&+)", self)
        zoom_in.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Plus))
        zoom_in.triggered.connect(lambda: self._web_view.setZoomFactor(self._web_view.zoomFactor() + 0.1))
        view_menu.addAction(zoom_in)

        zoom_out = QAction("縮小(&-)", self)
        zoom_out.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Minus))
        zoom_out.triggered.connect(lambda: self._web_view.setZoomFactor(self._web_view.zoomFactor() - 0.1))
        view_menu.addAction(zoom_out)

        zoom_reset = QAction("ズームリセット(&0)", self)
        zoom_reset.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_0))
        zoom_reset.triggered.connect(lambda: self._web_view.setZoomFactor(1.0))
        view_menu.addAction(zoom_reset)

        # ヘルプメニュー
        help_menu = menu_bar.addMenu("ヘルプ(&H)")

        about_action = QAction("このアプリについて(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_toolbar(self):
        toolbar = self.addToolBar("メイン")
        toolbar.setMovable(False)

        open_btn = QAction("ファイルを開く", self)
        open_btn.triggered.connect(self._open_file)
        toolbar.addAction(open_btn)

        toolbar.addSeparator()

        for label, value in [("ライト", "light"), ("ダーク", "dark"), ("自動", "media")]:
            btn = QAction(label, self)
            btn.triggered.connect(lambda checked, v=value: self._set_appearance(v))
            toolbar.addAction(btn)

    # ── File Operations ──

    def _open_file(self):
        settings = QSettings()
        last_dir = settings.value("last_open_dir", "")
        filepath, _ = QFileDialog.getOpenFileName(
            self, "データファイルを開く", last_dir, FILTER_STRING
        )
        if not filepath:
            return
        self._load_and_display(filepath)

    def _load_and_display(self, filepath: str, spec: str = ""):
        try:
            df = load_file(filepath)
        except Exception as e:
            QMessageBox.critical(self, "ファイル読み込みエラー", str(e))
            return

        self._current_df = df
        self._current_file = filepath
        self._add_recent(filepath)

        settings = QSettings()
        settings.setValue("last_open_dir", str(Path(filepath).parent))

        rows, cols = df.shape
        fname = Path(filepath).name
        self._status_label.setText(f"{fname}  |  {rows:,} 行 x {cols} 列")
        self.setWindowTitle(f"{fname} - PyGWalker Desktop")

        self._start_server(df, spec=spec)

    def _start_server(self, df: pd.DataFrame, spec: str = ""):
        # Stop existing server
        if self._server is not None:
            self._server.stop()
            self._server = None

        self._server = ServerBridge(
            df,
            spec=spec,
            appearance=self._appearance,
            theme_key=self._theme_key,
            kernel_computation=None,  # auto-detect
            parent=self,
        )
        self._server.server_ready.connect(self._on_server_ready)
        self._server.server_error.connect(self._on_server_error)
        self._server.start()

    def _on_server_ready(self, url: str):
        self._web_view.load_url(url)

    def _on_server_error(self, error: str):
        QMessageBox.critical(self, "サーバーエラー", f"PyGWalkerの起動に失敗しました:\n{error}")

    # ── Theme ──

    def _set_appearance(self, appearance: str):
        self._appearance = appearance
        for value, action in self._theme_actions.items():
            action.setChecked(value == appearance)

        QSettings().setValue("appearance", appearance)

        # Restart server with new appearance if data is loaded
        if self._current_df is not None:
            self._start_server(self._current_df)

    # ── Spec Export/Import ──

    def _export_spec(self):
        if self._server is None:
            QMessageBox.information(self, "設定エクスポート", "データが読み込まれていません。")
            return
        # TODO: walkerのupdate_specコールバックからspecをキャプチャ
        QMessageBox.information(self, "設定エクスポート", "設定エクスポート機能は今後のアップデートで対応予定です。")

    def _import_spec(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "設定をインポート", "", "JSON ファイル (*.json);;すべてのファイル (*)"
        )
        if not filepath and self._current_file:
            return
        if self._current_df is not None:
            spec_text = Path(filepath).read_text(encoding="utf-8")
            self._start_server(self._current_df, spec=filepath)

    # ── Recent Files ──

    def _add_recent(self, filepath: str):
        settings = QSettings()
        recent = settings.value("recent_files", []) or []
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        recent = recent[:_MAX_RECENT]
        settings.setValue("recent_files", recent)
        self._update_recent_menu()

    def _update_recent_menu(self):
        self._recent_menu.clear()
        settings = QSettings()
        recent = settings.value("recent_files", []) or []
        for filepath in recent:
            action = QAction(Path(filepath).name, self)
            action.setToolTip(filepath)
            action.triggered.connect(lambda checked, fp=filepath: self._load_and_display(fp))
            self._recent_menu.addAction(action)
        self._recent_menu.setEnabled(bool(recent))

    # ── About ──

    def _show_about(self):
        QMessageBox.about(
            self,
            "PyGWalker Desktop について",
            "PyGWalker Desktop v0.1.0\n\n"
            "オープンソースのTableau風データ可視化アプリです。\n"
            "PyGWalker と PySide6 で構築されています。",
        )

    # ── Window Geometry ──

    def _restore_geometry(self):
        settings = QSettings()
        geometry = settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        QSettings().setValue("window_geometry", self.saveGeometry())
        if self._server is not None:
            self._server.stop()
        event.accept()
