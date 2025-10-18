import json
from pathlib import Path

import pytest

from nifi_automation import controller_registry as registry


def _descriptor_stub() -> dict:
    return {
        "schema-write-strategy": {
            "displayName": "Schema Write Strategy",
            "allowableValues": [
                {"allowableValue": {"value": "no-schema", "displayName": "Do Not Write Schema"}},
                {"allowableValue": {"value": "embed-avro-schema", "displayName": "Embed Avro Schema"}},
            ],
        },
        "schema-access-strategy": {
            "displayName": "Schema Access Strategy",
            "allowableValues": [
                {"allowableValue": {"value": "infer-schema", "displayName": "Infer Schema"}},
                {"allowableValue": {"value": "schema-text-property", "displayName": "Use 'Schema Text' Property"}},
            ],
        },
    }


class TestNormaliseProperties:
    def test_translates_display_name_and_value(self):
        descriptors = _descriptor_stub()
        properties = {
            "Schema Write Strategy": "Do Not Write Schema",
            "Schema Access Strategy": "Infer Schema",
        }

        normalised = registry._normalise_properties(properties, descriptors)

        assert normalised["schema-write-strategy"] == "no-schema"
        assert normalised["schema-access-strategy"] == "infer-schema"

    def test_prefers_display_key_when_requested(self):
        descriptors = _descriptor_stub()
        properties = {"schema-write-strategy": "Embed Avro Schema"}

        normalised = registry._normalise_properties(properties, descriptors, prefer_display=True)

        assert "Schema Write Strategy" in normalised
        assert normalised["Schema Write Strategy"] == "embed-avro-schema"

    def test_accepts_slug_alias(self):
        descriptors = _descriptor_stub()
        properties = {"schema_write_strategy": "Do Not Write Schema"}

        normalised = registry._normalise_properties(properties, descriptors)

        assert normalised["schema-write-strategy"] == "no-schema"

    def test_raises_on_unknown_keys(self):
        descriptors = _descriptor_stub()
        properties = {"custom-property": "abc123"}

        with pytest.raises(registry.ControllerServiceProvisioningError):
            registry._normalise_properties(properties, descriptors)

    def test_empty_properties_returns_empty_dict(self):
        descriptors = _descriptor_stub()

        assert registry._normalise_properties({}, descriptors) == {}


def test_manifest_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    manifest_path = tmp_path / "controller-services.json"
    monkeypatch.setattr(registry, "MANIFEST_PATH", manifest_path)

    # Initial load should create the manifest file and return no entries.
    entries = registry._load_manifest_entries()
    assert entries == []
    assert manifest_path.exists()

    entry = registry.ControllerServiceEntry(
        key="json-writer",
        name="JsonRecordSetWriter",
        type="org.apache.nifi.json.JsonRecordSetWriter",
        properties={"schema-write-strategy": "no-schema"},
        auto_enable=False,
        bundle={"group": "org.apache.nifi", "artifact": "nifi-json-nar", "version": "2.0.0"},
        id="1234-abc",
    )

    registry._save_manifest_entries([entry])

    reloaded = registry._load_manifest_entries()
    assert len(reloaded) == 1
    loaded_entry = reloaded[0]
    assert loaded_entry.key == entry.key
    assert loaded_entry.auto_enable is False
    assert loaded_entry.properties == entry.properties
    assert loaded_entry.id == entry.id

    with manifest_path.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)
    saved_entry = payload["controller_services"][0]
    assert saved_entry["id"] == "1234-abc"
    assert saved_entry["properties"]["schema-write-strategy"] == "no-schema"
    assert saved_entry["auto_enable"] is False
