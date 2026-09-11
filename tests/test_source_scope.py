from plainchange.project_declarations import extract_declared_capabilities
from plainchange.source_scope import is_supported_source_path


def test_source_scope_supports_modern_javascript_and_excludes_dependencies():
    assert is_supported_source_path("frontend/src/Card.vue")
    assert is_supported_source_path("frontend/tests/card.test.mjs")
    assert is_supported_source_path("scripts/build.cjs")
    assert not is_supported_source_path("frontend/node_modules/pkg/index.js")
    assert not is_supported_source_path("vendor/pkg/client.py")
    assert not is_supported_source_path("dist/app.js")


def test_markdown_capability_table_prefers_semantic_column_over_count():
    declarations = [
        {
            "path": "README.md",
            "source_ref": "git:abc:README.md",
            "text": """
## 主要功能

| 模块 | 数量 | 覆盖功能 |
| --- | ---: | --- |
| 会员 | 4 | 会员查询、资料维护和状态管理 |
| 订单 | 5 | 订单查询、退款和履约跟踪 |
| 商品 | 3 | 商品搜索、库存和推荐说明 |
""",
        }
    ]
    items, _refs = extract_declared_capabilities(declarations)

    assert [item["label"] for item in items] == ["会员", "订单", "商品"]
    assert items[0]["description"] == "会员查询、资料维护和状态管理"
    assert items[1]["description"] != "5"
