import json
import time
from pathlib import Path

import pytest

from plainchange.onboarding import OnboardingState
from plainchange.system_flow import understand_system, entry_coverage, source_inventory
from test_onboarding import onboarding_server, _request
from test_system_flow import flow_repo, FixtureProvider
from conftest import run_git


def test_foreign_host_never_receives_session_token(onboarding_server, sample_repo):
    _, state, url = onboarding_server
    status, body, _ = _request(url + '/', extra_headers={'Host':'selftest.invalid'})
    assert status == 403 and state.token.encode() not in body
    status, _, _ = _request(url + '/api/repository', payload={'path':str(sample_repo[0])}, token=state.token,
                            extra_headers={'Host':'selftest.invalid','Origin':'http://selftest.invalid'})
    assert status == 403
    status, _, _ = _request(url + '/', extra_headers={'Host':'127.0.0.1:1'})
    assert status == 403


def test_jobs_are_authenticated_and_survive_new_page_request(onboarding_server, sample_repo, tmp_path):
    _, state, url = onboarding_server
    repo, base, head = sample_repo
    job = state.start_job({'repository':str(repo),'base':base,'head':head,'output':str(tmp_path/'reports')})
    assert _request(url+'/api/jobs')[0] == 403
    assert _request(url+'/')[0] == 200
    status, body, _ = _request(url+'/api/jobs', token=state.token)
    assert status == 200
    assert json.loads(body)['jobs'][0]['id'] == job.job_id
    wait_jobs([job])


def wait_jobs(jobs):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and any(j.status not in ('failed','succeeded') for j in jobs):
        time.sleep(.05)
    assert all(j.status == 'succeeded' for j in jobs), [j.error for j in jobs]


def test_real_concurrent_jobs_keep_their_own_task_evidence(sample_repo, tmp_path):
    repo, base, head = sample_repo
    state = OnboardingState()
    payload = {'repository':str(repo),'base':base,'head':head,'output':str(tmp_path/'reports')}
    jobs = [state.start_job(dict(payload,task=marker)) for marker in ['request-alpha','request-beta']]
    wait_jobs(jobs)
    assert jobs[0].output != jobs[1].output
    before = (jobs[0].output/'review.html').read_bytes()
    for job, marker in zip(jobs, ['request-alpha','request-beta']):
        evidence = json.loads((job.output/'evidence.json').read_text(encoding='utf-8'))
        assert next(e['content'] for e in evidence['evidence'] if e['id']=='task.original') == marker
    retry = state.start_job(dict(payload,task='request-third'))
    wait_jobs([retry])
    assert (jobs[0].output/'review.html').read_bytes() == before


def test_invalid_system_output_returns_json_and_no_job(onboarding_server, sample_repo, tmp_path):
    _, state, url = onboarding_server
    status, body, _ = _request(url+'/api/understand', token=state.token, payload={
        'repository':str(sample_repo[0]),'output':{'bad':True},'model_config':str(tmp_path/'missing.json')})
    assert status == 400 and json.loads(body)['ok'] is False
    assert not state.jobs


def test_model_can_recover_from_denied_read_without_expanding_access(flow_repo, tmp_path):
    class Recover(FixtureProvider):
        def complete(self, system, packet, schema, folder):
            if 'reads' in schema['properties'] and 'round' in packet and 'findings' not in packet:
                if packet['round'] == 1:
                    folder.mkdir(parents=True)
                    return {'reads':[{'path':'../auth.json','start_line':1}]}
                assert packet['denied_reads'][0]['reason'] == 'outside_source_scope'
                assert all(s['path'] != '../auth.json' for s in packet['sources'])
                packet = dict(packet, round=packet['round']-1)
            return super().complete(system, packet, schema, folder)
    result = understand_system(flow_repo, output=tmp_path/'recovered', provider=Recover())
    doc = json.loads(Path(result['system_flow']).read_text(encoding='utf-8'))
    assert len(doc['flows']) == 1
    assert doc['coverage']['denied_reads'][0]['reason'] == 'outside_source_scope'


def test_html_is_bounded_source_and_unmapped_entry_is_visible(flow_repo):
    (flow_repo/'index.html').write_text('<button id="analyze">Analyze</button>\n<button id="understand">Understand</button>',encoding='utf-8')
    run_git(flow_repo,'add','index.html')
    run_git(flow_repo,'commit','-m','two distinct entry points')
    inventory, _ = source_inventory(flow_repo, 'HEAD')
    assert 'index.html' in {r['path'] for r in inventory}
    source = {'id':'html','path':'index.html','start_line':1,'text':(flow_repo/'index.html').read_text()}
    doc = {'sources':[source],'flows':[{'id':'change','nodes':[{'evidence':[{'source_id':'html','start_line':1,'end_line':1}]}],'edges':[]}]}
    coverage = entry_coverage(doc)
    assert coverage['entries'][0]['flow_ids'] == ['change']
    assert coverage['entries'][1]['name'] == 'understand'
    assert coverage['entries'][1]['flow_ids'] == []
    assert coverage['semantic_completeness'] == 'not_verified'


def test_counterevidence_read_denial_is_bounded_and_report_can_finish(flow_repo, tmp_path):
    class ReviewRecover(FixtureProvider):
        def complete(self, system, packet, schema, folder):
            if 'reads' in schema['properties'] and 'findings' in packet:
                folder.mkdir(parents=True)
                if packet['round'] == 1:
                    return {'reads':[{'path':'../auth.json','start_line':1}]}
                assert packet['denied_reads'][-1]['reason'] == 'outside_source_scope'
                return {'reads':[]}
            return super().complete(system, packet, schema, folder)
    result = understand_system(flow_repo, output=tmp_path/'review-recovered', provider=ReviewRecover())
    doc = json.loads(Path(result['system_flow']).read_text(encoding='utf-8'))
    assert doc['product_review']['challenge']['status'] == 'model_reviewed_not_independently_verified'
    assert len(doc['coverage']['denied_reads']) == 1
