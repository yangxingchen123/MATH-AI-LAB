from tools.problem_validator.discovery import find_project_root
from tools.studio.app import handle_request
from tools.studio.catalog import build_catalog, get_document
from tools.studio.launch import is_serving, launch, studio_url
from tools.studio.render import extract_headings


def _root():
    return find_project_root()


def test_catalog_lists_real_objects_and_skips_sentinels():
    catalog = build_catalog(_root())
    problem_ids = {item["id"] for group in catalog["trees"]["problems"] for item in group["items"]}
    knowledge_ids = {item["id"] for group in catalog["trees"]["knowledge"] for item in group["items"]}
    method_ids = {item["id"] for group in catalog["trees"]["methods"] for item in group["items"]}
    project_ids = {item["id"] for group in catalog["trees"]["project"] for item in group["items"]}
    lab_ids = {item["id"] for group in catalog["trees"]["lab"] for item in group["items"]}
    assert "P0001" in problem_ids
    assert "P0002" in problem_ids
    assert "P0000" not in problem_ids
    assert "K0001" in knowledge_ids
    assert "K0002" in knowledge_ids
    assert "K0000" not in knowledge_ids
    assert "M0001" in method_ids
    assert "M0002" in method_ids
    assert "美赛2026-A" in project_ids
    assert "PROB-SF-001" in lab_ids
    assert catalog["writes"] is False


def test_problem_document_keeps_workflow_dir_separate_from_yaml_status():
    doc = get_document(_root(), "problem", "P0002")
    assert doc is not None
    assert doc["id"] == "P0002"
    assert doc["yaml_status"] == "reviewed"
    assert doc["workflow_dir"] == "已解决"
    assert doc["parts"] == ["a", "b", "c"]
    assert "φ(X)=AX-XB" in doc["title"] or "AX-XB" in doc["title"]
    assert "线性映射" in doc["body"]
    assert doc["kind_label"] == "习题 / 定理"
    assert doc["path"].startswith("02_题目库/")


def test_unknown_and_pathlike_ids_do_not_read_files():
    root = _root()
    assert get_document(root, "problem", "P9999") is None
    assert get_document(root, "problem", "../01_知识库/数学变换/勒让德变换.md") is None
    assert get_document(root, "problem", "..\\..\\元数据规范.md") is None


def test_http_is_read_only_and_serves_notebook_shell():
    root = _root()
    home = handle_request("GET", "/", {}, root=root)
    assert home.status == 200
    assert "text/html" in home.content_type
    assert b"MATH-AI-LAB" in home.body

    catalog = handle_request("GET", "/api/catalog", {}, root=root)
    assert catalog.status == 200
    assert b"P0002" in catalog.body

    doc = handle_request("GET", "/api/doc", {"kind": "problem", "id": "P0002"}, root=root)
    assert doc.status == 200
    assert b"reviewed" in doc.body

    missing = handle_request("GET", "/api/doc", {"kind": "problem", "id": "P9999"}, root=root)
    assert missing.status == 404

    traversal = handle_request(
        "GET",
        "/api/doc",
        {"kind": "problem", "id": "../../元数据规范.md"},
        root=root,
    )
    assert traversal.status == 404

    posted = handle_request("POST", "/api/catalog", {}, root=root)
    assert posted.status == 405

    put = handle_request("PUT", "/api/doc", {"kind": "problem", "id": "P0002"}, root=root)
    assert put.status == 405


def test_launch_reuses_running_server_and_never_writes(tmp_path):
    started = []
    opened = []
    result = launch(
        root=tmp_path,
        host="127.0.0.1",
        port=8765,
        open_browser=True,
        probe=lambda _url: True,
        start=lambda **kwargs: started.append(kwargs),
        browse=lambda url: opened.append(url),
    )
    assert result["status"] == "already_running"
    assert result["writes"] is False
    assert result["url"] == "http://127.0.0.1:8765/"
    assert started == []
    assert opened == ["http://127.0.0.1:8765/"]


def test_launch_starts_once_when_down(tmp_path):
    started = []
    result = launch(
        root=tmp_path,
        host="127.0.0.1",
        port=8765,
        open_browser=False,
        probe=lambda _url: False,
        start=lambda **kwargs: started.append(kwargs) or True,
        browse=lambda _url: None,
    )
    assert result["status"] == "started"
    assert result["writes"] is False
    assert started == [{"root": tmp_path, "host": "127.0.0.1", "port": 8765}]


def test_probe_closed_port():
    assert studio_url("127.0.0.1", 8765) == "http://127.0.0.1:8765/"
    assert is_serving("http://127.0.0.1:9/", timeout=0.2) is False


def test_extract_headings_skips_yaml_and_keeps_h2():
    body = "---\nid: P0002\n---\n# Title\n\n## 题目\n\n$$\\varphi(X)=AX-XB.$$\n\n## 解答\n"
    heads = extract_headings(body)
    assert [h["text"] for h in heads] == ["题目", "解答"]
    assert heads[0]["id"] == "题目"


def test_problem_body_is_markdown_without_front_matter():
    p2 = get_document(_root(), "problem", "P0002")
    assert p2 is not None
    assert not p2["body"].lstrip().startswith("---")
    assert "schema_version:" not in p2["body"].split("## 题目", 1)[0]
    assert "$$\\varphi(X)=AX-XB.$$" in p2["body"] or "\\varphi(X)=AX-XB" in p2["body"]
    texts = [h["text"] for h in p2["headings"]]
    assert "题目" in texts
    assert "解答" in texts
    p1 = get_document(_root(), "problem", "P0001")
    assert p1 is not None
    assert "一、原题" in [h["text"] for h in p1["headings"]]


def test_vendor_katex_is_offline():
    root = _root()
    home = handle_request("GET", "/", {}, root=root)
    assert home.status == 200
    assert b"cdn.jsdelivr" not in home.body
    assert b"cdnjs.cloudflare" not in home.body
    assert b"/vendor/katex.min.js" in home.body
    assert b"/vendor/katex.min.css" in home.body
    js = handle_request("GET", "/vendor/katex.min.js", {}, root=root)
    assert js.status == 200
    assert len(js.body) > 10_000
    css = handle_request("GET", "/vendor/katex.min.css", {}, root=root)
    assert css.status == 200
    font = handle_request(
        "GET",
        "/vendor/fonts/KaTeX_Main-Regular.woff2",
        {},
        root=root,
    )
    assert font.status == 200
    assert handle_request("GET", "/vendor/../app.js", {}, root=root).status == 404
    assert handle_request("GET", "/vendor/katex.min.exe", {}, root=root).status == 404
