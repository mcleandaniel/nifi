---
claims:
  claim-bundle-modules:
    sources:
      - source-bundle-pom
  claim-python-version:
    sources:
      - source-python-runtime
  claim-per-processor-env:
    sources:
      - source-python-runtime
  claim-bridge-start:
    sources:
      - source-bridge-start
  claim-discover-config:
    sources:
      - source-bridge-discover
  claim-discover-nar:
    sources:
      - source-bridge-nar
  claim-process-lifecycle:
    sources:
      - source-bridge-process
  claim-pythonprocess-gateway:
    sources:
      - source-pythonprocess-gateway
  claim-dependency-package:
    sources:
      - source-python-deps-package
  claim-dependency-class:
    sources:
      - source-python-deps-processor
  claim-dependency-isolation:
    sources:
      - source-python-deps-isolation
  claim-nar-layout:
    sources:
      - source-python-nar-layout
  claim-deployment-dir:
    sources:
      - source-python-deploy
  claim-venv-location:
    sources:
      - source-python-venv
  claim-sample-processor:
    sources:
      - source-write-message
  claim-sample-requirements:
    sources:
      - source-multi-req
  claim-python-reload:
    sources:
      - source-python-reload
  claim-python-devdir:
    sources:
      - source-python-reload
  claim-python-clean-env:
    sources:
      - source-python-venv
  claim-reference-guide:
    sources:
      - source-python-intro
sources:
  source-bundle-pom:
    title: "nifi-py4j-extension-bundle/pom.xml"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/pom.xml"
    locator: "L25-L33"
  source-bridge-start:
    title: "StandardPythonBridge"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-py4j-bridge/src/main/java/org/apache/nifi/py4j/StandardPythonBridge.java"
    locator: "L65-L92"
  source-bridge-discover:
    title: "StandardPythonBridge"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-py4j-bridge/src/main/java/org/apache/nifi/py4j/StandardPythonBridge.java"
    locator: "L95-L103"
  source-bridge-nar:
    title: "StandardPythonBridge"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-py4j-bridge/src/main/java/org/apache/nifi/py4j/StandardPythonBridge.java"
    locator: "L262-L270"
  source-bridge-process:
    title: "StandardPythonBridge"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-py4j-bridge/src/main/java/org/apache/nifi/py4j/StandardPythonBridge.java"
    locator: "L217-L283"
  source-pythonprocess-gateway:
    title: "PythonProcess"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-py4j-bridge/src/main/java/org/apache/nifi/py4j/PythonProcess.java"
    locator: "L102-L175"
  source-python-runtime:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L640-L645"
  source-python-deps-package:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L672-L687"
  source-python-deps-processor:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L690-L714"
  source-python-deps-isolation:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L723-L730"
  source-python-nar-layout:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L732-L747"
  source-python-deploy:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L753-L781"
  source-python-venv:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L788-L794"
  source-python-reload:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L650-L662"
  source-write-message:
    title: "WriteMessage.py"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-python-test-extensions/src/main/resources/extensions/WriteMessage.py"
    locator: "L16-L34"
  source-multi-req:
    title: "requirements.txt (multi-processor test extensions)"
    location: "nifi-extension-bundles/nifi-py4j-extension-bundle/nifi-python-test-extensions/src/main/resources/extensions/multi-processor/requirements.txt"
    locator: "L16-L16"
  source-python-intro:
    title: "NiFi Python Developer's Guide"
    location: "nifi-docs/src/main/asciidoc/python-developer-guide.adoc"
    locator: "L25-L35"
---

## Overview
<span id="claim-bundle-modules">The `nifi-py4j-extension-bundle` aggregator groups bridge code, the deployable NAR, Python test extensions, and integration tests under a single Maven parent.</span>
<span id="claim-python-version">NiFi's Python API requires Python 3.9, 3.10, 3.11, or 3.12 on the host running the processors.</span>
<span id="claim-per-processor-env">On first use of a processor type, NiFi provisions a dedicated environment for that implementation and installs its declared dependencies into it.</span>

## Concepts / Architecture
<span id="claim-bridge-start">`StandardPythonBridge` keeps process configuration and controller-service lookups, launches a persistent controller Python process, and registers log listeners before reporting itself ready.</span>
<span id="claim-discover-config">During discovery it constructs the list of Python extension directories from the configured locations and delegates the scan to the controller process.</span>
<span id="claim-discover-nar">When starting new Python processes the bridge augments the discovery paths with Python-capable NAR directories so packaged extensions load beside source directories.</span>
<span id="claim-process-lifecycle">Processor creation reuses non-isolated processes when possible, enforces both per-type and global Python process limits, and picks between bundled homes and versioned work directories for virtual environments.</span>
<span id="claim-pythonprocess-gateway">Each `PythonProcess` establishes the Py4J gateway with authentication tokens, launches the Python runtime, waits for a ping acknowledgement, and registers log listeners before exposing the controller API.</span>

## Implementation / Configuration
<span id="claim-dependency-package">Package-style processor bundles should include a package-level `requirements.txt` so NiFi installs dependencies once per package.</span>
<span id="claim-dependency-class">Standalone processors declare third-party libraries through the `ProcessorDetails.dependencies` list, which NiFi feeds to pip for that processor's environment.</span>
<span id="claim-dependency-isolation">Dependency isolation ensures each processor type and version receives its own virtual environment, preventing cross-version dependency leakage.</span>
<span id="claim-nar-layout">For air-gapped deployments, bundle processors as NAR archives that contain a manifest, a `bundled-dependencies/` directory, and the processor source at the archive root.</span>
<span id="claim-deployment-dir">Without a NAR, copy processor source into the configured `python/extensions` directories—subdirectories group multi-module packages—and include the `Java` inner class so discovery succeeds.</span>
<span id="claim-venv-location">NiFi stores the per-processor environments under `work/python/extensions/<Processor>/<version>` unless `nifi.python.working.directory` points elsewhere.</span>

## Usage / Examples
<span id="claim-sample-processor">The `WriteMessage` sample processor demonstrates the mandatory `Java` interface declaration, `ProcessorDetails` metadata, and a `transform` implementation returning a `FlowFileTransformResult`.</span>

```python
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult

class WriteMessage(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        version = '0.0.1-SNAPSHOT'

    def transform(self, context, flowfile):
        return FlowFileTransformResult(relationship="success", contents="Hello, World")
```

<span id="claim-sample-requirements">A multi-processor test package ships a `requirements.txt` that pins dependencies such as `charset-normalizer==3.4.0`, illustrating how to capture Python requirements alongside processors.</span>

```text
charset-normalizer==3.4.0
```

```bash
# Deploy a processor module
cp MyProcessor.py "$NIFI_HOME/python/extensions/"
```

## Best Practices / Tips
<span id="claim-python-reload">During development you can change processor code, stop and start it, or use “Run Once” to reload changes without restarting NiFi, provided the initial load succeeded.</span>
<span id="claim-python-devdir">Add your development source directory to the configured extension directories so NiFi reloads updates directly from your workspace.</span>

## Troubleshooting
<span id="claim-python-clean-env">If a virtual environment becomes out of sync, stop NiFi, remove the processor's environment directory, and NiFi will rebuild it on the next start.</span>

## Reference / Related Docs
<span id="claim-reference-guide">The NiFi Python Developer's Guide offers broader coverage of Python processor development patterns beyond this Py4J integration overview.</span>
