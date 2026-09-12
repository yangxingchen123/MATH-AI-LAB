from tools.problem_validator.discovery import find_project_root
from tools.studio.render import strip_front_matter
from tools.qt_workbench.markdown import VENDOR_DIR, render_body_html, render_reading_page


def test_reading_html_renders_headings_and_math_tokens():
    source = """## 五、有效域

凸分析常讨论扩展实值函数

$$f:\\mathbb{R}^{n}\\to\\mathbb{R}\\cup\\{+\\infty\\}.$$

其**有效域**定义为 $\\operatorname{dom} f$。
"""
    html = render_body_html(source)
    assert "<h2>" in html
    assert "五、有效域" in html
    assert "## 五" not in html
    assert "<strong>有效域</strong>" in html
    assert 'class="math-display"' in html
    assert r"\mathbb{R}" in html
    assert r"\operatorname{dom} f" in html
    page = render_reading_page(source, dark=True)
    assert "katex.min.js" in page
    assert "file:" in page
    assert "renderMathInElement" in page
    assert VENDOR_DIR.joinpath("katex.min.js").is_file()
    assert VENDOR_DIR.joinpath("auto-render.min.js").is_file()


def test_math_subscripts_are_not_turned_into_emphasis():
    html = render_body_html(r"设 $f_1$ 与 **有效域**。")
    assert "<em>" not in html
    assert "$f_1$" in html
    assert "<strong>有效域</strong>" in html


def test_code_fences_keep_dollar_signs():
    html = render_body_html("```\n$x$\n```\n\n$y$")
    assert "<pre>" in html
    assert "$x$" in html
    assert "$y$" in html


def test_convex_knowledge_article_is_not_raw_markdown():
    path = find_project_root() / "01_知识库" / "优化理论" / "凸函数.md"
    body = strip_front_matter(path.read_text(encoding="utf-8"))
    html = render_body_html(body)
    assert "五、有效域" in html
    assert "## 五、有效域" not in html
    assert "<h2>" in html
    assert 'class="math-display"' in html
    assert r"\operatorname{dom} f" in html
