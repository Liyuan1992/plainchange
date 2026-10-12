import gzip
import hashlib
import json
from importlib import resources

from plainchange.system_flow import render_flow


def test_bundled_viewer_identity_license_and_compiled_slots():
    assets = resources.files('plainchange').joinpath('assets')
    blob = assets.joinpath('archify-viewer.html.gz').read_bytes()
    manifest = json.loads(assets.joinpath('archify-viewer.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(blob).hexdigest() == manifest['sha256']
    viewer = gzip.decompress(blob).decode('utf-8')
    assert viewer.count('__PC_SVG__') == 1
    assert '__PC_TITLE__' in viewer
    assert '{{i18n:' not in viewer
    assert 'id="btn-theme"' in viewer
    assert 'MIT License' in assets.joinpath('ARCHIFY-LICENSE.txt').read_text(encoding='utf-8')


def test_report_bundles_viewer_offline_and_keeps_untrusted_json_inert():
    document = {'title':'Test <script>alert(1)</script>', 'flows':[]}
    output = render_flow(document)
    assert 'id="archify-template"' in output
    assert 'sandbox="allow-scripts allow-downloads"' in output
    assert 'allow-same-origin' not in output
    assert 'connect-src \'none\'' in output
    assert 'Test <script>' not in output
    assert '\\u003cscript>' in output
    assert '__ARCHIFY_VIEWER__' not in output
    assert '__ARCHIFY_LICENSE__' not in output
