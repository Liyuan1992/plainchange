from plainchange.auto_draft import _specific_audience_candidate


def test_specific_audience_candidate_requires_a_role_and_evidence():
    assert _specific_audience_candidate(
        {
            "role": "门店店员",
            "reason": "推荐卡片会出现在店员使用的经营看板中。",
            "evidence_ids": ["git.file.001"],
        }
    ) == {
        "role": "门店店员",
        "reason": "推荐卡片会出现在店员使用的经营看板中。",
        "evidence_ids": ["git.file.001"],
    }
    assert _specific_audience_candidate(
        {"role": "普通用户", "reason": "没有具体角色。", "evidence_ids": ["git.file.001"]}
    ) is None
    assert _specific_audience_candidate(
        {"role": "门店店员", "reason": "有角色但没有来源。", "evidence_ids": []}
    ) is None
