"""Visual tokens. Academic workspace, not a marketing shell."""

from __future__ import annotations

LIGHT = {
    "bg": "#f3efe6",
    "sidebar": "#e8e2d6",
    "list": "#f7f3ea",
    "paper": "#fffdf8",
    "ink": "#1c1b17",
    "muted": "#6d6a62",
    "faint": "#8d8980",
    "line": "#d8d0c4",
    "accent": "#2f4a6e",
    "accent_soft": "#e4edf6",
    "chip": "#efe8db",
    "danger": "#8a2b2b",
    "danger_soft": "#f3e4e4",
    "ok": "#2f6b4f",
    "ok_soft": "#e4efe8",
    "hover": "#efe9dc",
    "primary": "#2f4a6e",
    "primary_ink": "#fffdf8",
    "topbar": "#efe9dc",
    "card": "#f7f3ea",
}

DARK = {
    "bg": "#0e1014",
    "sidebar": "#151820",
    "list": "#12151c",
    "paper": "#1b1f28",
    "ink": "#e8eaed",
    "muted": "#9aa3b2",
    "faint": "#6d7585",
    "line": "#2a3140",
    "accent": "#4c8dff",
    "accent_soft": "#1c2f4d",
    "chip": "#222836",
    "danger": "#f07178",
    "danger_soft": "#3a2224",
    "ok": "#8fcdb0",
    "ok_soft": "#1b2a22",
    "hover": "#1e2430",
    "primary": "#4c8dff",
    "primary_ink": "#ffffff",
    "topbar": "#12151c",
    "card": "#161a22",
}


def build_qss(t: dict[str, str]) -> str:
    return f"""
QMainWindow {{
  background: {t["bg"]};
  color: {t["ink"]};
}}
QWidget {{
  color: {t["ink"]};
  font-size: 13px;
}}
QFrame#sidebar {{
  background: {t["sidebar"]};
  border: none;
  border-right: 1px solid {t["line"]};
}}
QFrame#listPane {{
  background: {t["list"]};
  border: none;
  border-right: 1px solid {t["line"]};
}}
QFrame#reader {{
  background: {t["paper"]};
  border: none;
}}
QFrame#homePanel, QFrame#docPanel {{
  background: {t["paper"]};
}}
QLabel#brandMark {{
  color: {t["accent"]};
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
}}
QLabel#brandName {{
  font-size: 16px;
  font-weight: 650;
}}
QLabel#brandHint {{
  color: {t["muted"]};
  font-size: 11px;
}}
QLabel#sectionKicker {{
  color: {t["accent"]};
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.6px;
}}
QLabel#titleLabel {{
  font-size: 22px;
  font-weight: 650;
  letter-spacing: -0.3px;
}}
QLabel#mutedLabel, QLabel#pathLabel {{
  color: {t["muted"]};
  font-size: 12px;
}}
QLabel#pathLabel {{
  font-family: Consolas, "Cascadia Mono", monospace;
}}
QLabel#listHeading {{
  font-size: 15px;
  font-weight: 650;
}}
QLabel#listCount {{
  color: {t["muted"]};
  font-size: 11px;
}}
QLabel#chip {{
  background: {t["chip"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 11px;
}}
QLabel#idText {{
  color: {t["accent"]};
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 11px;
  font-weight: 600;
}}
QLabel#rowTitle {{
  font-size: 13px;
}}
QLabel#rowMeta {{
  color: {t["faint"]};
  font-size: 11px;
}}
QFrame#objectRow {{
  background: transparent;
  border: none;
  border-bottom: 1px solid {t["line"]};
}}
QFrame#objectRow[selected="true"] {{
  background: {t["accent_soft"]};
}}
QFrame#countCard {{
  background: {t["chip"]};
  border: 1px solid {t["line"]};
  border-radius: 10px;
}}
QFrame#countCard:hover {{
  border-color: {t["accent"]};
}}
QLabel#countValue {{
  font-size: 22px;
  font-weight: 650;
}}
QLabel#countName {{
  color: {t["muted"]};
  font-size: 12px;
}}
QTreeWidget {{
  background: transparent;
  border: none;
  outline: none;
  padding: 4px 10px 12px 10px;
  show-decoration-selected: 0;
}}
QTreeWidget::item {{
  height: 28px;
  padding: 2px 10px;
  border-radius: 6px;
  color: {t["ink"]};
}}
QTreeWidget::item:hover {{
  background: {t["hover"]};
}}
QTreeWidget::item:selected {{
  background: {t["accent"]};
  color: {t["paper"]};
}}
QTreeWidget::item:disabled {{
  color: {t["faint"]};
}}
QTreeWidget::branch {{
  image: none;
  border: none;
  background: transparent;
}}
QListWidget {{
  background: transparent;
  border: none;
  outline: none;
  padding: 0;
}}
QListWidget::item {{
  margin: 0;
  padding: 0;
}}
QListWidget::item:selected {{
  background: transparent;
}}
QLineEdit#searchField {{
  background: {t["paper"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 7px 10px;
  selection-background-color: {t["accent_soft"]};
}}
QLineEdit#searchField:focus {{
  border-color: {t["accent"]};
}}
QComboBox#modelCombo, QComboBox#settingsCombo, QComboBox#workflowCombo, QComboBox#partCombo, QComboBox#outcomeCombo, QComboBox#promoteType {{
  background: {t["paper"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 6px 10px;
  min-height: 20px;
}}
QComboBox#modelCombo {{
  min-width: 188px;
}}
QComboBox#settingsCombo {{
  min-height: 28px;
}}
QComboBox#modelCombo:focus, QComboBox#settingsCombo:focus, QLineEdit#customModel:focus, QLineEdit#gptPrompt:focus, QPlainTextEdit#gptTranscript:focus {{
  border-color: {t["accent"]};
}}
QComboBox#modelCombo:hover, QComboBox#settingsCombo:hover, QComboBox#workflowCombo:hover, QComboBox#partCombo:hover, QComboBox#outcomeCombo:hover, QComboBox#promoteType:hover {{
  border-color: {t["accent"]};
}}
QComboBox QAbstractItemView {{
  background: {t["paper"]};
  color: {t["ink"]};
  selection-background-color: {t["accent_soft"]};
  border: 1px solid {t["line"]};
}}
QLineEdit#customModel {{
  background: {t["paper"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 7px 10px;
}}
QTextBrowser {{
  background: {t["paper"]};
  color: {t["ink"]};
  border: none;
  padding: 8px 4px 24px 4px;
  font-size: 15px;
}}
QWidget#markdownReader {{
  background: {t["paper"]};
  border: none;
}}
QPushButton#ghostButton, QPushButton#exploreSearchBtn {{
  background: transparent;
  color: {t["muted"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 6px 12px;
}}
QPushButton#ghostButton:hover, QPushButton#exploreSearchBtn:hover {{
  color: {t["ink"]};
  border-color: {t["accent"]};
}}
QStatusBar {{
  background: {t["sidebar"]};
  color: {t["muted"]};
  border-top: 1px solid {t["line"]};
  font-size: 11px;
}}
QStatusBar::item {{
  border: none;
}}
QSplitter::handle {{
  background: {t["line"]};
  width: 1px;
}}
QScrollBar:vertical {{
  background: transparent;
  width: 10px;
  margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
  background: {t["line"]};
  border-radius: 4px;
  min-height: 32px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
  height: 0;
}}
QFrame#topbar {{
  background: {t["topbar"]};
  border: none;
  border-bottom: 1px solid {t["line"]};
}}
QLabel#topContext {{
  color: {t["muted"]};
  font-size: 12px;
}}
QPushButton#primaryButton, QPushButton#labEvaluateBtn {{
  background: {t["primary"]};
  color: {t["primary_ink"]};
  border: none;
  border-radius: 8px;
  padding: 7px 14px;
  font-weight: 600;
}}
QPushButton#primaryButton:disabled, QPushButton#labEvaluateBtn:disabled {{
  background: {t["chip"]};
  color: {t["faint"]};
}}
QPushButton#primaryButton:hover:!disabled, QPushButton#labEvaluateBtn:hover:!disabled {{
  background: {t["accent"]};
}}
QPlainTextEdit#sourceEditor {{
  background: {t["bg"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 12px;
  font-family: Consolas, "Cascadia Mono", "Microsoft YaHei UI", monospace;
  font-size: 13px;
  selection-background-color: {t["accent_soft"]};
}}
QTabWidget::pane {{
  border: none;
  background: {t["paper"]};
}}
QTabBar::tab {{
  background: transparent;
  color: {t["muted"]};
  padding: 8px 14px;
  border: none;
  border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
  color: {t["ink"]};
  border-bottom: 2px solid {t["accent"]};
}}
QLabel#editHint {{
  color: {t["muted"]};
  font-size: 11px;
}}
QScrollArea#actionScroll {{
  background: {t["paper"]};
  border: none;
}}
QLineEdit#field, QLineEdit#failureSearch, QLineEdit#labSet, QPlainTextEdit#field, QPlainTextEdit#labResult, QSpinBox {{
  background: {t["paper"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 8px;
  padding: 7px 10px;
  selection-background-color: {t["accent_soft"]};
}}
QPlainTextEdit#field, QPlainTextEdit#labResult {{
  font-family: Consolas, "Cascadia Mono", "Microsoft YaHei UI", monospace;
  font-size: 13px;
}}
QFrame#settingsCard {{
  background: {t["card"]};
  border: 1px solid {t["line"]};
  border-radius: 14px;
}}
QLabel#cardTitle {{
  font-size: 16px;
  font-weight: 650;
  letter-spacing: -0.2px;
}}
QLabel#formLabel {{
  color: {t["muted"]};
  font-size: 11px;
  font-weight: 600;
}}
QLabel#statusBadge {{
  background: {t["chip"]};
  color: {t["muted"]};
  border: 1px solid {t["line"]};
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
}}
QLabel#statusBadge[tone="ok"] {{
  background: {t["ok_soft"]};
  color: {t["ok"]};
  border-color: {t["ok_soft"]};
}}
QLabel#statusBadge[tone="err"] {{
  background: {t["danger_soft"]};
  color: {t["danger"]};
  border-color: {t["danger_soft"]};
}}
QLabel#statusBadge[tone="idle"] {{
  background: {t["chip"]};
  color: {t["muted"]};
}}
QLabel#statusNote[tone="err"] {{
  color: {t["danger"]};
}}
QPlainTextEdit#gptTranscript {{
  background: {t["paper"]};
  color: {t["ink"]};
  border: 1px solid {t["line"]};
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13px;
  font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
}}
QFrame#composerBar {{
  background: {t["paper"]};
  border: 1px solid {t["line"]};
  border-radius: 10px;
}}
QLineEdit#gptPrompt {{
  background: transparent;
  color: {t["ink"]};
  border: none;
  padding: 8px 10px;
}}
QLabel#topContext {{
  font-size: 13px;
  color: {t["ink"]};
}}
"""


LIGHT_QSS = build_qss(LIGHT)
DARK_QSS = build_qss(DARK)
