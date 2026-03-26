"""QThread-based server bridge managing PygWalker + HTTPServer lifecycle."""

import socketserver
from http.server import HTTPServer
from typing import Optional

import pandas as pd
from PySide6.QtCore import QThread, Signal

from pygwalker.api.pygwalker import PygWalker
from pygwalker.communications.hacker_comm import BaseCommunication
from pygwalker.utils.free_port import find_free_port

from .handler import create_handler


class _QuietTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def server_close(self):
        super().server_close()


class ServerBridge(QThread):
    """Runs PygWalker HTTP server on a background thread."""

    server_ready = Signal(str)   # emits URL
    server_error = Signal(str)   # emits error message

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        spec: str = "",
        appearance: str = "media",
        theme_key: str = "g2",
        kernel_computation: Optional[bool] = None,
        default_tab: str = "vis",
        parent=None,
    ):
        super().__init__(parent)
        self._df = df
        self._spec = spec
        self._appearance = appearance
        self._theme_key = theme_key
        self._kernel_computation = kernel_computation
        self._default_tab = default_tab
        self._httpd: Optional[HTTPServer] = None

    def run(self):
        try:
            walker = PygWalker(
                gid=None,
                dataset=self._df,
                field_specs=[],
                spec=self._spec,
                source_invoke_code="",
                theme_key=self._theme_key,
                appearance=self._appearance,
                show_cloud_tool=False,
                use_preview=False,
                kernel_computation=self._kernel_computation,
                use_save_tool=True,
                gw_mode="explore",
                is_export_dataframe=True,
                kanaries_api_key="",
                default_tab=self._default_tab,
                cloud_computation=False,
            )
            walker._init_callback(BaseCommunication(str(walker.gid)))

            handler_class = create_handler(walker)
            port = find_free_port()

            self._httpd = _QuietTCPServer(("127.0.0.1", port), handler_class)
            self.server_ready.emit(f"http://127.0.0.1:{port}")
            self._httpd.serve_forever()
        except Exception as e:
            self.server_error.emit(str(e))

    def stop(self):
        """Thread-safe shutdown. Call from main thread."""
        if self._httpd:
            self._httpd.shutdown()
        self.wait(5000)
