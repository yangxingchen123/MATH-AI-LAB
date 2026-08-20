"""Constants for Knowledge Indexer v1.0."""

from __future__ import annotations

INDEXER_NAME = "Knowledge Indexer"
INDEXER_VERSION = "1.0"
INDEX_VERSION = 1

INDEX_DIR_NAME = "_索引"
INDEX_DIR_RELATIVE = "01_知识库/_索引"

MANAGED_FILES = (
    "README.md",
    "按领域.md",
    "关系索引.md",
    "knowledge_index.json",
)

GENERATED_BANNER = (
    "本目录由 Knowledge Indexer v1.0 自动生成。禁止手工维护。"
    "所有事实以 Knowledge Markdown YAML Metadata 为准；本目录可以删除并重新构建。"
)

RULES: dict[str, tuple[str, str]] = {
    "KI-ROOT-001": ("ERROR", "Invalid project root"),
    "KI-VALIDATE-001": ("ERROR", "Knowledge Validator failed; index not built"),
    "KI-VALIDATE-002": ("ERROR", "Strict warnings blocked indexing"),
    "KI-BUILD-001": ("ERROR", "Index model build failed"),
    "KI-RENDER-001": ("ERROR", "Index render failed"),
    "KI-IO-001": ("ERROR", "Index I/O failure"),
    "KI-PUBLISH-001": ("ERROR", "Transactional publish failed"),
    "KI-STALE-001": ("ERROR", "Expected generated file missing"),
    "KI-STALE-002": ("ERROR", "Generated file content differs"),
    "KI-STALE-003": ("ERROR", "Unexpected file exists in generated index directory"),
}
