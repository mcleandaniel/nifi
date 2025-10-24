# GitHub Actions CI/CD for NiFi Automation

- Status: Draft
- Owner: @dmclean
- Approvers: TBD
- Links: TBD
- Date: 2025-10-24

## Context

The NiFi automation project currently lacks automated CI/CD, requiring manual validation of Python code quality, test execution, and flow spec correctness. Every PR merge carries risk without automated validation. Contributors must remember to run linters, tests, and validation scripts locally—creating friction and increasing the chance of breaking changes reaching main.

GitHub Actions provides free CI for public repos and integrates seamlessly with PR workflows. We need phased adoption: start with fast unit tests and static analysis, then add full integration tests with a containerized NiFi instance once the baseline pipeline is stable.

## Goals / Non‑Goals

### Goals
- Automated validation on every PR and push to main
- Python code quality checks (linting, formatting, type checking)
- Fast feedback loop (<5 minutes for unit tests)
- Pytest execution with proper test categorization (unit vs integration)
- YAML/JSON syntax validation for flow specs
- Clear pass/fail status visible in GitHub PR UI
- Foundation for future NiFi integration tests via Docker

### Non‑Goals
- Full integration testing with NiFi in Phase 1 (deferred to Phase 2)
- Performance benchmarking
- Deployment automation (beyond testing)
- Multi-region or complex infrastructure
- Security scanning (can add later as separate workflow)

## Current Architecture (as‑is)

### Test Structure
Tests live under `automation/tests/` with the following organization:
- Unit tests: `test_*.py` files testing individual modules without external dependencies
- Integration tests: `tests/integration/test_*_live.py` requiring a running NiFi instance
- Flow tests: `tests/flows/<WorkflowName>/test_*.py` requiring deployed flows

### Test Markers
Existing pytest markers indicate test requirements:
```python
@pytest.mark.integration  # Requires NiFi instance
pytestmark = pytest.mark.integration
pytestmark = [pytest.mark.integration, pytest.mark.tools]
```

### Manual Workflow
Currently developers must:
1. Activate virtualenv: `source automation/.venv/bin/activate`
2. Run linters manually (if at all)
3. Execute tests: `python -m pytest automation/tests`
4. Validate YAML specs manually
5. Hope nothing breaks in CI (which doesn't exist yet)

### Dependencies
- Python 3.13
- uv for package management
- pytest for testing
- httpx, pydantic, typer, pyyaml (runtime deps)
- Docker for NiFi (integration tests only)

## Proposal (to‑be)

### Phase 1: Core CI - Tests & Validation (No NiFi Required)

Focus: Get fast, reliable test validation running in GitHub Actions.

#### Workflow File: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Create virtualenv and install dependencies
        run: |
          uv venv automation/.venv
          source automation/.venv/bin/activate
          uv pip install -e automation/.[dev]
      
      - name: Validate YAML/JSON files
        run: |
          source automation/.venv/bin/activate
          python automation/scripts/validate_all_specs.py
      
      - name: Run unit tests
        run: |
          source automation/.venv/bin/activate
          python -m pytest automation/tests \
            -v \
            -m "not integration" \
            --maxfail=5 \
            --tb=short \
            --junit-xml=test-results.xml
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: test-results.xml
```

### Phase 1b: Code Quality - Linting & Type Checking (Future)

After Phase 1 stabilizes, add:
- Linting with ruff or flake8
- Type checking with mypy
- Code formatting checks with black/ruff format
- Import sorting with isort/ruff

These are valuable but not blocking for initial CI setup.

### Phase 2: Integration Tests with Docker NiFi (Future)

#### Workflow File: `.github/workflows/integration.yml`

```yaml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  # Can also trigger manually
  workflow_dispatch:

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    services:
      nifi:
        image: apache/nifi:latest
        ports:
          - 8443:8443
        env:
          SINGLE_USER_CREDENTIALS_USERNAME: admin
          SINGLE_USER_CREDENTIALS_PASSWORD: changemechangeme
        options: >-
          --health-cmd "curl -k https://localhost:8443/nifi"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 30
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          uv venv automation/.venv
          source automation/.venv/bin/activate
          uv pip install -e automation/.[dev]
      
      - name: Wait for NiFi to be ready
        run: |
          timeout 300 bash -c 'until curl -k https://localhost:8443/nifi-api/system-diagnostics; do sleep 5; done'
      
      - name: Configure .env for tests
        run: |
          cat > .env << EOF
          NIFI_BASE_URL=https://localhost:8443/nifi-api
          NIFI_USERNAME=admin
          NIFI_PASSWORD=changemechangeme
          NIFI_VERIFY_SSL=false
          EOF
      
      - name: Run integration tests
        run: |
          source automation/.venv/bin/activate
          python -m pytest automation/tests \
            -v \
            -m "integration" \
            --maxfail=3 \
            --tb=short \
            --junit-xml=integration-results.xml
      
      - name: Upload integration results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: integration-test-results
          path: integration-results.xml
```

### API/Schema Changes

#### New Script: `automation/scripts/validate_all_specs.py`
```python
"""Validate all YAML/JSON specs for syntax and structure."""
import sys
from pathlib import Path
import yaml
import json

def validate_yaml(path: Path) -> bool:
    try:
        with open(path) as f:
            yaml.safe_load(f)
        return True
    except Exception as e:
        print(f"❌ {path}: {e}")
        return False

def validate_json(path: Path) -> bool:
    try:
        with open(path) as f:
            json.load(f)
        return True
    except Exception as e:
        print(f"❌ {path}: {e}")
        return False

def main():
    repo_root = Path(__file__).parent.parent.parent
    automation = repo_root / "automation"
    
    failures = 0
    
    # Validate flow YAMLs
    for yaml_file in automation.glob("flows/**/*.yaml"):
        if not validate_yaml(yaml_file):
            failures += 1
    
    # Validate manifest JSON
    manifest = automation / "manifest" / "controller-services.json"
    if not validate_json(manifest):
        failures += 1
    
    if failures:
        print(f"\n❌ {failures} validation error(s)")
        sys.exit(1)
    else:
        print("✓ All specs valid")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

#### Pytest Configuration: `automation/pytest.ini`
Already exists but should be enhanced:
```ini
[pytest]
markers =
    integration: tests requiring a live NiFi instance (deselect with '-m "not integration"')
    tools: tests for tooling workflows
    slow: tests that take >10 seconds

# Default options
addopts = 
    -ra
    --strict-markers
    --strict-config
    --tb=short

# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Coverage (optional)
# addopts = --cov=nifi_automation --cov-report=term-missing
```

### Algorithms / Components

#### Test Categorization Strategy
1. **Unit tests** (no marker): Fast, no external deps, can run in any environment
   - Examples: `test_config.py`, `test_flow_spec_loader.py`, `test_cli_dispatch.py`
   - Run on every commit
   
2. **Integration tests** (`@pytest.mark.integration`): Require NiFi instance
   - Examples: `test_live_nifi.py`, `test_cli_admin_ops_live.py`
   - Run on demand or scheduled (Phase 2)
   
3. **Tools tests** (`@pytest.mark.tools`): May require additional setup
   - Can be combined with integration marker
   - Run selectively

#### CI Trigger Strategy
- **On PR**: Run unit tests + linting (fast feedback)
- **On merge to main**: Run unit tests + linting
- **Nightly/On-demand**: Run full integration suite with NiFi (Phase 2)
- **Manual**: Allow workflow_dispatch for debugging

### Compatibility / Migration

**Backwards Compatibility**: No breaking changes. Tests run the same locally and in CI.

**Feature Flags**: Use pytest markers to gradually expand CI coverage:
- Phase 1: `-m "not integration"` skips NiFi tests
- Phase 2: Remove marker filter to run all tests

**Defaults**: CI runs automatically on PR creation/update. Integration tests opt-in initially.

## Testing Plan

### Validation of the CI Pipeline Itself
1. Create a test PR with intentional failures:
   - Syntax error in Python
   - Invalid YAML in a flow spec
   - Failing unit test
   - Verify CI catches each

2. Create a test PR with all passing checks:
   - Verify green checkmark appears
   - Verify test results artifact uploads

3. Test integration workflow locally:
   ```bash
   docker run -d -p 8443:8443 \
     -e SINGLE_USER_CREDENTIALS_USERNAME=admin \
     -e SINGLE_USER_CREDENTIALS_PASSWORD=changemechangeme \
     apache/nifi:latest
   
   # Wait for startup, then:
   source automation/.venv/bin/activate
   python -m pytest automation/tests -m integration
   ```

### Success Criteria
- ✅ CI runs complete in <5 minutes for unit tests
- ✅ All existing unit tests pass in CI
- ✅ PR status checks reflect test results
- ✅ Invalid YAML/JSON is caught before merge
- ✅ Test artifacts available for download

## Rollout Plan

### Phase 1: Core CI - Tests & Validation (Week 1)
**Goal**: Get basic automated testing running

1. **Day 1-2**: 
   - Create `.github/workflows/ci.yml`
   - Add `validate_all_specs.py` script
   - Enhance `pytest.ini` with markers
   
2. **Day 3-4**:
   - Test workflow on feature branch
   - Fix any issues discovered
   - Verify all unit tests pass
   
3. **Day 5-7**:
   - Merge to main
   - Enable branch protection requiring CI
   - Monitor first few PRs
   - Document CI in README

### Phase 1b: Code Quality - Linting (Week 2)
**Goal**: Add code quality checks without blocking progress

1. Add linting configuration
2. Run linters on codebase and fix issues
3. Add linting step to CI workflow
4. Consider auto-formatting options

### Phase 2: Integration Tests (Weeks 3-4)
**Goal**: Full end-to-end testing with NiFi

1. **Week 3**:
   - Create `.github/workflows/integration.yml`
   - Test Docker service configuration
   - Validate NiFi startup reliability
   - Run on schedule (nightly)
   
2. **Week 4**:
   - Enable integration tests on main branch merges
   - Document troubleshooting for flaky tests
   - Consider making integration tests optional for PRs

### Guardrails
- Keep Phase 1 minimal to avoid blocking PRs
- Monitor CI minutes usage (free tier limits)
- Document opt-out path if CI blocks urgent fixes
- Provide override mechanism for maintainers

### Observability
- GitHub Actions tab shows all runs
- Test artifacts downloadable for 90 days
- Failure notifications via GitHub
- Track CI duration trends (should stay <5 min)

### Revert Plan
- Delete workflow file to disable
- Update branch protection to remove required checks
- Continue manual testing until CI fixed

## Risks & Mitigations

### Risk: Flaky Integration Tests
**Impact**: High - blocks PRs, frustrates contributors  
**Mitigation**: 
- Phase 1 doesn't include integration tests
- Phase 2 uses health checks and retries
- Mark flaky tests with `@pytest.mark.flaky` (requires plugin)
- Integration tests optional initially

### Risk: Docker NiFi Startup Reliability
**Impact**: Medium - inconsistent CI results  
**Mitigation**:
- Use official `apache/nifi` image
- Implement robust health checking
- Increase timeout to 5 minutes for startup
- Document known issues and workarounds

### Risk: CI Minutes Exhaustion (Free Tier)
**Impact**: Medium - CI stops running  
**Mitigation**:
- Monitor usage dashboard
- Optimize test speed (parallel execution)
- Run integration tests less frequently (nightly, not per-PR)
- Consider self-hosted runners if needed

### Risk: Python 3.13 Availability
**Impact**: Low - older Python in CI  
**Mitigation**:
- `actions/setup-python@v5` supports 3.13
- Pin specific version in workflow
- Test with 3.12 fallback if needed

### Risk: Breaking Changes to pytest.ini
**Impact**: Low - local tests affected  
**Mitigation**:
- Test changes in isolated branch
- Document marker usage clearly
- Maintain backwards compatibility

### Risk: Stale Dependencies in CI Cache
**Impact**: Low - unexpected failures  
**Mitigation**:
- Use `uv` which handles dependency resolution
- Don't cache venv in Phase 1 (fast enough without)
- Add cache invalidation strategy if caching added

## Alternatives Considered

### Alternative 1: Use CircleCI or Travis CI
**Rejected**: GitHub Actions is free for public repos, better integration with GitHub features, no third-party account needed.

### Alternative 2: Run Integration Tests in Every PR
**Rejected**: Too slow (>5 min), consumes CI minutes, blocks quick iterations. Better to run nightly or on-demand.

### Alternative 3: Use Tox for Test Environments
**Rejected**: `uv` is faster and simpler. Tox adds complexity without clear benefit for single-Python-version project.

### Alternative 4: Skip YAML Validation in CI
**Rejected**: YAML errors are common and easy to catch. Validation script is trivial and fast.

### Alternative 5: Use Docker Compose for NiFi
**Considered**: Provides more control over networking and volumes. May revisit in Phase 2 if service definition insufficient. For now, GitHub service containers are simpler.

## Open Questions

1. **Code coverage requirements**: Minimum threshold?
   - **Decision needed**: Measure current coverage first
   - **Recommendation**: Track coverage but don't block PRs initially

4. **Integration test frequency**: Nightly? On main branch only?
   - **Decision needed**: Monitor CI minutes usage
   - **Recommendation**: Start with nightly, evaluate after 2 weeks

5. **Self-hosted runners**: Need for performance or Docker socket access?
   - **Decision needed**: Wait until Phase 2 integration tests to assess
   - **Recommendation**: Use GitHub-hosted unless issues arise

6. **Artifact retention**: 90 days default, is that enough?
   - **Decision needed**: Monitor storage usage
   - **Recommendation**: 90 days is fine, reduce if storage becomes issue

7. **Branch protection rules**: Which checks required vs optional?
   - **Decision needed**: After Phase 1 stabilizes
   - **Recommendation**: Make unit tests + validation required, integration optional

## Implementation Checklist

### Phase 1: Core CI - Tests & Validation
- [ ] Create `.github/workflows/ci.yml`
- [ ] Add `automation/scripts/validate_all_specs.py`
- [ ] Update `automation/pytest.ini` with markers
- [ ] Test workflow on feature branch
- [ ] Document CI setup in `automation/README.md`
- [ ] Enable branch protection requiring CI pass
- [ ] Add CI status badge to main README

### Phase 1b: Code Quality - Linting
- [ ] Choose linting tools (recommend: ruff)
- [ ] Add linting configuration files
- [ ] Run linters and fix existing issues
- [ ] Add linting step to CI workflow
- [ ] Consider auto-formatting on save
- [ ] Add type checking (mypy) if desired

### Phase 2: Integration Tests
- [ ] Create `.github/workflows/integration.yml`
- [ ] Test NiFi service container locally
- [ ] Configure NiFi health checks
- [ ] Add integration test documentation
- [ ] Schedule nightly runs
- [ ] Monitor and tune for flakiness
- [ ] Consider Docker Compose if needed

### Optional Enhancements
- [ ] Add code coverage reporting
- [ ] Create pre-commit hooks matching CI
- [ ] Add security scanning (bandit/safety)
- [ ] Implement test parallelization
- [ ] Add performance benchmarking
- [ ] Dependency vulnerability scanning

## Success Metrics

After Phase 1 (4 weeks):
- ✅ 100% of PRs have automated test validation
- ✅ <5% false positive rate (flaky tests)
- ✅ <5 minute average CI runtime
- ✅ Zero incidents of broken main branch
- ✅ >80% developer satisfaction (informal poll)

After Phase 2 (8 weeks):
- ✅ Integration tests run nightly without failures
- ✅ NiFi Docker startup succeeds >95% of time
- ✅ Integration test runtime <15 minutes
- ✅ CI minutes usage <50% of free tier limit
