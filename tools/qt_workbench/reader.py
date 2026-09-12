"""Reading pane: rendered Markdown + KaTeX, not source."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget

from .markdown import render_body_html, render_reading_page, vendor_href
from .style import DARK, LIGHT


def webengine_available() -> bool:
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
    except Exception:
        return False
    return True


class MarkdownReader(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("markdownReader")
        self.source = ""
        self.page_html = ""
        self.uses_webengine = False
        self._dark = True
        self._web = None
        self._browser: QTextBrowser | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        try:
            import os

            from PySide6.QtCore import QUrl
            from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
            from PySide6.QtWebEngineWidgets import QWebEngineView

            from .bootstrap import clear_webengine_guard, mark_webengine_starting, webengine_blocked

            if os.environ.get("MATH_AI_LAB_QT_NO_WEBENGINE") == "1" or webengine_blocked():
                raise RuntimeError("webengine disabled")

            mark_webengine_starting()
            class _LockedPage(QWebEnginePage):
                def acceptNavigationRequest(self, url, _nav_type, _main_frame):  # type: ignore[no-untyped-def]
                    return url.scheme() in {"file", "data", "about", "qrc", "blob"}

                def javaScriptConsoleMessage(self, *_args: object) -> None:
                    return

            view = QWebEngineView(self)
            page = _LockedPage(view)
            view.setPage(page)
            settings = view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
            )
            settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, False)
            self._web = view
            self._base = QUrl(vendor_href())
            self.uses_webengine = True
            layout.addWidget(view)
            clear_webengine_guard()
        except Exception:
            self._web = None
            self.uses_webengine = False
            browser = QTextBrowser(self)
            browser.setOpenExternalLinks(False)
            self._browser = browser
            layout.addWidget(browser)

    def set_markdown(self, source: str, *, dark: bool = True) -> None:
        self.source = source or ""
        self._dark = dark
        tokens = DARK if dark else LIGHT
        if self._web is not None:
            self.page_html = render_reading_page(self.source, dark=dark)
            self._web.page().setBackgroundColor(QColor(tokens["paper"]))
            self._web.setHtml(self.page_html, self._base)
            return
        body = render_body_html(self.source)
        self.page_html = (
            "<html><head><meta charset='utf-8'>"
            f"<style>body{{background:{tokens['paper']};color:{tokens['ink']};"
            "font-family:'Microsoft YaHei UI','Segoe UI',sans-serif;"
            "font-size:16px;line-height:1.7;}}</style></head>"
            f"<body>{body}</body></html>"
        )
        if self._browser is not None:
            self._browser.setHtml(self.page_html)
