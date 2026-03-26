"""QWebEngineView wrapper configured for PyGWalker."""

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView


class PygWalkerWebView(QWebEngineView):
    """WebView pre-configured for displaying PyGWalker UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._configure_settings()

    def _configure_settings(self):
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    def load_url(self, url: str):
        self.setUrl(QUrl(url))
