from __future__ import annotations

import pytest
from pathlib import Path

import yaml


pytestmark = pytest.mark.tools


def _load(path: str):
    data = yaml.safe_load(Path(path).read_text())
    assert isinstance(data, dict)
    return data


def test_trust_create_flow_structure():
    data = _load('automation/tools/flows/ops/trust_create_http.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Create_HTTP'
    names = {p['name'] for p in pg['processors']}
    assert {'HandleHttpRequest', 'Inject Key'} <= names


def test_trust_add_flow_structure():
    data = _load('automation/tools/flows/ops/trust_add_http.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Add_HTTP'
    names = {p['name'] for p in pg['processors']}
    assert {'HandleHttpRequest', 'Inject Key', 'Run (Groovy add)'} <= names


def test_trust_remove_flow_structure():
    data = _load('automation/tools/flows/ops/trust_remove_http.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Remove_HTTP'
    names = {p['name'] for p in pg['processors']}
    assert {'HandleHttpRequest', 'Inject Key'} <= names


def test_trust_inspect_flow_structure():
    data = _load('automation/tools/flows/ops/trust_inspect_http.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Inspect_HTTP'
    names = {p['name'] for p in pg['processors']}
    assert {'HandleHttpRequest', 'Inject Key'} <= names
