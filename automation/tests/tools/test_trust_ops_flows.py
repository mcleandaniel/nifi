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
    data = _load('automation/tools/flows/ops/trust_create.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Create'
    names = {p['name'] for p in pg['processors']}
    assert {'Trigger (create)', 'Params (create)', 'Exec (create)'} <= names


def test_trust_add_flow_structure():
    data = _load('automation/tools/flows/ops/trust_add.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Add'
    names = {p['name'] for p in pg['processors']}
    assert {'Trigger (add)', 'Params (add)', 'Exec (add)'} <= names


def test_trust_remove_flow_structure():
    data = _load('automation/tools/flows/ops/trust_remove.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Remove'
    names = {p['name'] for p in pg['processors']}
    assert {'Trigger (remove)', 'Params (remove)', 'Exec (remove)'} <= names


def test_trust_inspect_flow_structure():
    data = _load('automation/tools/flows/ops/trust_inspect.yaml')
    pg = data['process_group']['process_groups'][0]
    assert pg['name'] == 'Tools_Trust_Inspect'
    names = {p['name'] for p in pg['processors']}
    assert {'Trigger (inspect)', 'Params (inspect)', 'Exec (inspect)'} <= names
