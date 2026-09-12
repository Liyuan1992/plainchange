import copy
import json
from pathlib import Path

import pytest

from plainchange.models import ManifestError
from plainchange.report_localization import localized_control, text_locations, translation_template
from plainchange.report_localization import review_translation_template, review_text_locations, validated_review_translations
from test_software_control import software_control_sample
from test_software_control import resign
from test_review_model import validated_brief
from plainchange.review_model import build_beginner_review_model
from plainchange.cli import main
from plainchange.html_renderer import render_review_html
from plainchange.agent_provenance import GitAIProvenanceProvider


def pair():
    source = software_control_sample()
    pack = translation_template(source)
    pack['translations'] = {text: f'English explanation {i}' for i, text in enumerate(pack['translations'])}
    return source, pack


def test_projection_only_changes_presentation_and_preserves_source():
    source, pack = pair()
    original = copy.deepcopy(source)
    result = localized_control(source, pack)
    assert source == original
    for path, text in text_locations(source):
        parent = result
        for key in path[:-1]:
            parent = parent[key]
        assert parent[path[-1]] == pack['translations'][text]
        parent[path[-1]] = text
    assert result == source  # IDs, references, states, topology and source evidence unchanged.


@pytest.mark.parametrize('problem', ['missing', 'unknown', 'empty', 'chinese', 'identity', 'locale'])
def test_rejects_incomplete_stale_or_invalid_translation(problem):
    source, pack = pair()
    key = next(iter(pack['translations']))
    if problem == 'missing':
        del pack['translations'][key]
    elif problem == 'unknown':
        pack['translations']['control_identity'] = 'altered'
    elif problem == 'empty':
        pack['translations'][key] = ' '
    elif problem == 'chinese':
        pack['translations'][key] = 'English 中文'
    elif problem == 'identity':
        pack['control_identity'] = 'stale'
    else:
        pack['target_language'] = 'fr'
    with pytest.raises(ManifestError):
        localized_control(source, pack)


def test_vllm_pack_covers_all_owner_text():
    samples = Path(__file__).resolve().parents[1] / 'docs/product/samples'
    source = json.loads((samples / 'vllm-a69e75b-to-a85d073.software-control.json').read_text(encoding='utf-8'))
    pack = json.loads((samples / 'vllm-a69e75b-to-a85d073.translations.en.json').read_text(encoding='utf-8'))
    result = localized_control(source, pack)
    assert result['working_map']['nodes'][0]['id'] == source['working_map']['nodes'][0]['id']
    assert len(pack['translations']) > 100


def test_technical_translation_excludes_originals_and_nonpresentation_fields():
    model = {'review_identity': 'frozen', 'claims': [{'id': '证据ID', 'text': '待翻译',
             'original_text': '原始结论', 'evidence_ids': ['原始引用'], 'claim_type': 'unknown',
             'limitations': ['未运行']}], 'summary': [{'task_context': {'entries': [{'text': '用户原话'}]}}]}
    original = copy.deepcopy(model)
    supplement = review_translation_template(model)
    assert set(supplement['translations']) == {'待翻译', '未运行'}
    supplement['translations'] = {'待翻译': 'Not yet verified', '未运行': 'Not run'}
    pack = {'target_language': 'en', 'review_text': supplement}
    assert validated_review_translations(model, pack)['translations'] == supplement['translations']
    assert model == original
    assert all('original_text' not in path for path, _ in review_text_locations(model))
    for invalid in ['stale', 'missing', 'extra', 'chinese']:
        bad = copy.deepcopy(pack)
        if invalid == 'stale': bad['review_text']['review_identity'] = 'other'
        elif invalid == 'missing': del bad['review_text']['translations']['未运行']
        elif invalid == 'extra': bad['review_text']['translations']['原始结论'] = 'altered'
        else: bad['review_text']['translations']['未运行'] = '仍然中文'
        with pytest.raises(ManifestError): validated_review_translations(model, bad)


def test_cli_export_apply_preserves_canonical_data_and_rejects_stale_pack(tmp_path):
    import re
    model = build_beginner_review_model(validated_brief())
    control = software_control_sample()
    control['source_identity']['review_identity'] = model['review_identity']
    control = resign(control)
    for filename, value in [('beginner-review.json', model), ('software-control.json', control)]:
        (tmp_path / filename).write_text(json.dumps(value), encoding='utf-8')
    provenance = GitAIProvenanceProvider(command_prefix=(str(tmp_path / 'missing-git-ai'),)).collect(
        tmp_path,
        'a' * 40,
        'b' * 40,
        expected_added_lines=3,
        expected_deleted_lines=1,
    )
    (tmp_path / 'agent-provenance.json').write_text(json.dumps(provenance), encoding='utf-8')
    source_bytes = (tmp_path / 'software-control.json').read_bytes()
    pack_path = tmp_path / 'translation.json'
    assert main(['localize-report', str(tmp_path), '--export', str(pack_path)]) == 0
    pack = json.loads(pack_path.read_text(encoding='utf-8'))
    pack['translations'] = {text: f'Translated text {i}' for i, text in enumerate(pack['translations'])}
    pack['review_text']['translations'] = {text: f'Technical explanation {i}' for i, text in enumerate(pack['review_text']['translations'])}
    pack_path.write_text(json.dumps(pack), encoding='utf-8')
    assert main(['localize-report', str(tmp_path), '--translations', str(pack_path)]) == 0
    html = (tmp_path / 'review.html').read_text(encoding='utf-8')
    def embedded(identifier):
        return json.loads(re.search(r'<script id="' + identifier + r'" type="application/json">(.*?)</script>', html, re.S).group(1))
    assert embedded('software-control-data') == control
    assert embedded('localized-control-data')['en'] == localized_control(control, pack)
    assert embedded('agent-provenance-data') == provenance
    assert (tmp_path / 'software-control.json').read_bytes() == source_bytes
    pack['control_identity'] = 'stale'
    pack_path.write_text(json.dumps(pack), encoding='utf-8')
    assert main(['localize-report', str(tmp_path), '--translations', str(pack_path)]) != 0
    assert (tmp_path / 'review.html').read_text(encoding='utf-8') == html


def test_reviewed_pack_overrides_automatic_owner_projection():
    import re
    model = build_beginner_review_model(validated_brief())
    control = software_control_sample()
    control['source_identity']['review_identity'] = model['review_identity']
    control['presentation'] = {
        'schema_version': 'plainchange.owner-presentation.v1',
        'source_language': 'zh-CN',
        'messages': [{
            'path': ['first_screen_summary', 'headline'],
            'key': 'state.confirmed',
            'args': {},
        }],
        'source_language_paths': [['product', 'purpose']],
    }
    control = resign(control)
    pack = translation_template(control)
    pack['translations'] = {
        text: f'Reviewed English {index}'
        for index, text in enumerate(pack['translations'])
    }
    pack['review_text'] = review_translation_template(model)
    pack['review_text']['translations'] = {
        text: f'Reviewed technical English {index}'
        for index, text in enumerate(pack['review_text']['translations'])
    }

    html = render_review_html(model, control, pack)
    embedded = json.loads(re.search(
        r'<script id="localized-control-data" type="application/json">(.*?)</script>',
        html,
        re.S,
    ).group(1))

    assert embedded['en']['first_screen_summary']['headline'] == pack['translations'][
        control['first_screen_summary']['headline']
    ]
    assert embedded['en']['first_screen_summary']['headline'] != 'Confirmed'
