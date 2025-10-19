#!/usr/bin/env python3
import json
import os
import subprocess
import sys

def log(msg): print(f"[INFO] {msg}")

def err(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve(path):
    if os.path.isfile(path):
        return path
    for cand in [os.path.join("kb", path), os.path.join("kb", "plans", path)]:
        if os.path.isfile(cand):
            return cand
    base = os.path.basename(path)
    for cand in [f"kb/plans/{base}", f"plans/{base}"]:
        if os.path.isfile(cand):
            return cand
    return None

def render_prompt(scope, plan_id, topic):
    tid = topic.get("id","")
    title = topic.get("title","")
    summary = topic.get("summary","")
    category = topic.get("category","")
    priority = topic.get("priority","")
    tags = ", ".join(topic.get("tags",[]))
    req = topic.get("research_request","")
    sources = topic.get("recommended_sources",[]) or []
    src_block = "\n".join(f"- {s}" for s in sources) if sources else "- None specified"

    full_id = f"{plan_id}_{tid}"
    return f"""# Task
{req}

# Context
Scope: {scope}
Plan ID: {plan_id}
Topic ID: {full_id}
Category: {category}
Priority: {priority}
Tags: {tags}
Recommended Sources:
{src_block}

# Objective
{summary}

# Title
{title}

---
Provide a comprehensive, evidence-based response using the context above.
"""

def main():
    PLANS_DIR = "kb/plans"
    INDEX = f"{PLANS_DIR}/index.json"
    OUT_PROMPTS = "kb/drafts"
    OUT_OUTPUTS = "kb/generated"

    ensure_dir(OUT_PROMPTS)
    ensure_dir(OUT_OUTPUTS)

    if not os.path.isfile(INDEX):
        err(f"Missing {INDEX}")

    index = load_json(INDEX)
    plans = index.get("plans", [])
    if not plans:
        err("No plans in index.json")

    for entry in plans:
        path = entry.get("path")
        if not path or os.path.basename(path) == "index.json":
            continue
        plan_file = resolve(path)
        if not plan_file:
            err(f"Cannot find {path}")
        plan = load_json(plan_file)
        scope = plan.get("scope")
        topics = plan.get("topics", [])
        if not scope or not isinstance(topics, list):
            err(f"Invalid plan file: {plan_file}")

        plan_id = os.path.splitext(os.path.basename(plan_file))[0]
        log(f"Processing plan: {plan_id} ({len(topics)} topics)")

        for i, topic in enumerate(topics, 1):
            tid = topic.get("id")
            if not tid:
                continue
            full_id = f"{plan_id}_{tid}"

            prompt_text = render_prompt(scope, plan_id, topic)

            prompt_dir = os.path.join(OUT_PROMPTS, scope, plan_id)
            out_dir = os.path.join(OUT_OUTPUTS, scope, plan_id)
            ensure_dir(prompt_dir)
            ensure_dir(out_dir)

            prompt_path = os.path.join(prompt_dir, f"{full_id}.md")
            output_path = os.path.join(out_dir, f"{full_id}.md")

            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(prompt_text)

            log(f"  [{i}/{len(topics)}] {full_id}")
            # Simple call: codex exec "<prompt>"
            subprocess.run(["codex", "exec", prompt_text], stdout=open(output_path, "w"))

    log("Done.")

if __name__ == "__main__":
    main()

