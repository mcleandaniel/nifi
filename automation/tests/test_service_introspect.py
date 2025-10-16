import json

import pytest

from nifi_automation.service_introspect import (
    collect_controller_service_requirements,
    format_requirements_as_json,
    format_requirements_as_markdown,
)


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class _FakeHttpClient:
    def __init__(self, responses):
        self._responses = responses
        self.called = []

    def get(self, path):
        if path not in self._responses:
            raise AssertionError(f"Unexpected request path: {path}")
        self.called.append(path)
        return _FakeResponse(self._responses[path])


class _FakeNiFiClient:
    def __init__(self, responses):
        self._client = _FakeHttpClient(responses)


@pytest.fixture
def fake_nifi_client():
    types_payload = {
        "controllerServiceTypes": [
            {
                "type": "org.example.RequiredService",
                "bundle": {"group": "org.example", "artifact": "example-nar", "version": "1.0.0"},
                "description": "Example service",
            }
        ]
    }

    definition_payload = {
        "propertyDescriptors": {
            "Schema Access Strategy": {
                "name": "schema-access-strategy",
                "displayName": "Schema Access Strategy",
                "description": "How to obtain the schema.",
                "required": True,
                "defaultValue": "schema-name",
                "allowableValues": [
                    {
                        "allowableValue": {
                            "value": "schema-name",
                            "displayName": "Use 'Schema Name' Property",
                            "description": "Lookup by schema name.",
                        }
                    },
                    {
                        "allowableValue": {
                            "value": "schema-text-property",
                            "displayName": "Use 'Schema Text' Property",
                            "description": "Provide schema text.",
                        }
                    },
                ],
            },
            "Optional Property": {
                "name": "optional-property",
                "displayName": "Optional Property",
                "required": False,
            },
        }
    }

    encoded_type = "org.example.RequiredService"
    definition_path = (
        "/flow/controller-service-definition/"
        "org.example/example-nar/1.0.0/"
        + encoded_type
    )

    responses = {
        "/flow/controller-service-types": types_payload,
        definition_path: definition_payload,
    }
    return _FakeNiFiClient(responses)


def test_collect_controller_service_requirements_extracts_required_properties(fake_nifi_client):
    requirements = collect_controller_service_requirements(fake_nifi_client)
    assert len(requirements) == 1
    requirement = requirements[0]
    assert requirement["type"] == "org.example.RequiredService"

    props = requirement["requiredProperties"]
    assert len(props) == 1, "Only the required descriptor should be included"
    prop = props[0]
    assert prop["name"] == "schema-access-strategy"
    assert prop["displayName"] == "Schema Access Strategy"
    assert prop["defaultValue"] == "schema-name"
    assert len(prop["allowableValues"]) == 2
    assert prop["allowableValues"][0]["value"] == "schema-name"


def test_format_requirements_as_json_round_trips(fake_nifi_client):
    requirements = collect_controller_service_requirements(fake_nifi_client)
    json_text = format_requirements_as_json(requirements)
    parsed = json.loads(json_text)
    assert parsed[0]["requiredProperties"][0]["name"] == "schema-access-strategy"


def test_format_requirements_as_markdown_contains_table(fake_nifi_client):
    requirements = collect_controller_service_requirements(fake_nifi_client)
    markdown_text = format_requirements_as_markdown(requirements)
    assert "### `org.example.RequiredService`" in markdown_text
    assert "| `schema-access-strategy` | Schema Access Strategy" in markdown_text
