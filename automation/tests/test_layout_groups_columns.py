from __future__ import annotations

import textwrap
from pathlib import Path

from nifi_automation.flow_builder import load_flow_spec


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "spec.yaml"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def test_group_aware_layout_columns(tmp_path: Path):
    # default group has 1 PG; Group A has 4; Group B has 7
    spec_path = _write(
        tmp_path,
        """
        process_group:
          name: NiFi Flow
          process_groups:
            - name: DefaultOne
              processors: []
              connections: []
          groups:
            - name: Group A
              process_groups:
                - name: A1
                  processors: []
                  connections: []
                - name: A2
                  processors: []
                  connections: []
                - name: A3
                  processors: []
                  connections: []
                - name: A4
                  processors: []
                  connections: []
            - name: Group B
              process_groups:
                - name: B1
                  processors: []
                  connections: []
                - name: B2
                  processors: []
                  connections: []
                - name: B3
                  processors: []
                  connections: []
                - name: B4
                  processors: []
                  connections: []
                - name: B5
                  processors: []
                  connections: []
                - name: B6
                  processors: []
                  connections: []
                - name: B7
                  processors: []
                  connections: []
        """,
    )
    spec = load_flow_spec(spec_path)
    children = spec.root_group.child_groups
    # Build column sets by x coordinate buckets
    positions = {c.name: (c.position or (0.0, 0.0)) for c in children}
    # Extract representative x per column using name->col mapping from spec
    cols = spec.root_child_columns or {}
    xs = {}
    for name, col in cols.items():
        xs.setdefault(col, set()).add(positions[name][0])
    # Columns should be increasing x left->right
    xs_list = [min(v) for k, v in sorted(xs.items())]
    assert all(xs_list[i] < xs_list[i+1] for i in range(len(xs_list)-1)), xs_list
    # Within Group A (col=1), width (x lanes) should be <= 2 up to 10 items
    a_xs = sorted({positions[n][0] for n, c in cols.items() if c == 1})
    assert len(a_xs) <= 2
    # Within Group B (col=2), width (x lanes) should be <= 3
    b_xs = sorted({positions[n][0] for n, c in cols.items() if c == 2})
    assert len(b_xs) <= 3

