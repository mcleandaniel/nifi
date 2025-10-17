import pytest

from nifi_automation.flow_builder import (
    FlowDeploymentError,
    compute_auto_terminate_relationships,
    determine_controller_service_requirements,
    validate_and_normalize_properties,
)


def test_validate_and_normalize_properties_trims_and_allows_allowed_values():
    descriptors = {
        "Mode": {
            "allowableValues": [
                {"value": "ADVANCED", "displayName": "Advanced"},
                {"value": "BASIC", "displayName": "Basic"},
            ],
        },
        "RequiredProp": {"required": True},
    }

    props = {"Mode": "Advanced", "RequiredProp": "  value "}
    normalized = validate_and_normalize_properties(
        "TestProc",
        "org.example.Proc",
        props,
        descriptors,
        supports_dynamic_properties=False,
    )

    assert normalized["Mode"] == "ADVANCED"
    assert normalized["RequiredProp"] == "value"


def test_validate_and_normalize_properties_missing_required():
    descriptors = {"RequiredProp": {"required": True}}

    with pytest.raises(FlowDeploymentError):
        validate_and_normalize_properties(
            "TestProc",
            "org.example.Proc",
            {},
            descriptors,
            supports_dynamic_properties=False,
        )


def test_validate_and_normalize_properties_disallows_invalid_allowable():
    descriptors = {
        "Mode": {
            "allowableValues": [
                {"value": "A", "displayName": "Option A"},
                {"value": "B", "displayName": "Option B"},
            ]
        }
    }

    with pytest.raises(FlowDeploymentError):
        validate_and_normalize_properties(
            "TestProc",
            "org.example.Proc",
            {"Mode": "C"},
            descriptors,
            supports_dynamic_properties=False,
        )


def test_determine_controller_service_requirements_detects_missing_reference():
    descriptors = {
        "service": {
            "typeProvidedByValue": {
                "group": "org.apache.nifi",
                "artifact": "nifi-services",
                "version": "1.0.0",
                "type": "org.example.Controller",
            },
            "required": True,
        },
    }
    requirements = determine_controller_service_requirements("proc-1", descriptors, {})
    assert len(requirements) == 1
    requirement = requirements[0]
    assert requirement.processor_key == "proc-1"
    assert requirement.service_type == "org.example.Controller"


def test_compute_auto_terminate_relationships_respects_defaults_and_connections():
    relationships = [
        {"name": "success"},
        {"name": "failure"},
        {"name": "retry"},
    ]
    connected = {"success"}

    inferred = compute_auto_terminate_relationships("TestProc", [], relationships, connected)
    assert inferred == ["failure", "retry"]

    with pytest.raises(FlowDeploymentError):
        compute_auto_terminate_relationships("TestProc", ["unknown"], relationships, connected)


def test_compute_auto_terminate_relationships_rejects_connected_auto_terminate():
    relationships = [{"name": "success"}]
    connected = {"success"}
    with pytest.raises(FlowDeploymentError):
        compute_auto_terminate_relationships("TestProc", ["success"], relationships, connected)


def test_validate_and_normalize_properties_accepts_display_name_alias():
    descriptors = {
        "record-reader": {
            "displayName": "Record Reader",
        },
        "record-writer": {
            "displayName": "Record Writer",
        },
    }
    props = {"Record Reader": "reader-service", "record-writer": "writer-service"}
    normalized = validate_and_normalize_properties(
        "AliasProc",
        "org.example.RecordProc",
        props,
        descriptors,
        supports_dynamic_properties=False,
    )
    assert normalized["record-reader"] == "reader-service"
    assert normalized["record-writer"] == "writer-service"


def test_validate_and_normalize_properties_detects_duplicate_aliases():
    descriptors = {
        "record-reader": {
            "displayName": "Record Reader",
        },
    }
    props = {
        "record-reader": "reader-service",
        "Record Reader": "reader-service-2",
    }
    with pytest.raises(FlowDeploymentError):
        validate_and_normalize_properties(
            "AliasProc",
            "org.example.RecordProc",
            props,
            descriptors,
            supports_dynamic_properties=False,
        )
