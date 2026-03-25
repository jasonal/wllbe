# Outline Approval Hardening Implementation Plan

I'm using the writing-plans skill to create the implementation plan.
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the outline approval flow so artifact validation and existence checks are enforced, and failures propagate to the CLI with test coverage.

**Architecture:** ProjectStore maps artifact types to deterministic paths; validation and existence checks should live in ProjectStore, while the CLI simply surfaces any approval errors to the user. Tests exercise both unit logic and CLI failure modes without touching parsing or generation.

**Tech Stack:** Python 3.11 via the repository virtualenv, pytest for tests, standard library for filesystem checks.

---

### Task 1: Tighten ProjectStore approval validation

**Files:**
- Modify: `src/wllbe/projects/store.py`
- Test: `tests/unit/test_project_store.py`

- [ ] **Step 1: Write the failing test**

```python
def test_approve_artifact_rejects_invalid_artifact_name():
    store = ProjectStore(root="/tmp/project")
    with pytest.raises(ValueError):
        store.approve_artifact("chapter", "../secret.txt", target="foo")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_project_store.py -q -k invalid_artifact_name`
Expected: FAIL because we currently do not validate artifact names and allow path traversal.

- [ ] **Step 3: Write minimal implementation**

Add explicit allow-list inside `ProjectStore.approve_artifact` so only `chapter-outline` and `page-outline` are accepted, and ensure the generated artifact exists before copying.

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_project_store.py -q -k invalid_artifact_name`
Expected: PASS, confirming validation and existence check.

### Task 2: Add negative CLI coverage for approval failures

**Files:**
- Modify: `src/wllbe/cli.py`
- Test: `tests/unit/test_cli.py`

- [ ] **Step 1: Write the failing test**

```
def test_cli_approve_rejects_missing_artifact(tmp_path, capsys):
    project_store = mock_project_store()
    # configure to raise FileNotFoundError
    cli_obj = CLI(...)
    with pytest.raises(SystemExit):
        cli_obj.approve(project_id, "chapter", "chapter-outline")
    assert "generated artifact" in capsys.readouterr().err
```
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_cli.py -q -k approve_missing`
Expected: FAIL because CLI currently crashes or prints stack trace.

- [ ] **Step 3: Write minimal implementation**

Update CLI approval command to catch FileNotFoundError/ValueError from ProjectStore, print a clean error, and exit with non-zero status.

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_cli.py -q -k approve_missing`
Expected: PASS.

### Task 3: Validate missing generated artifact scenario

**Files:**
- Modify: `tests/unit/test_project_store.py`

- [ ] **Step 1: Write failing test**

```
def test_approve_artifact_missing_generated_file(tmp_path):
    store = ProjectStore(root=str(tmp_path))
    (tmp_path / "chapter-outline").write_text("approved")
    with pytest.raises(FileNotFoundError):
        store.approve_artifact("chapter", "chapter-outline", target="chapter-outline")
```
```

- [ ] **Step 2: Run test**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_project_store.py -q -k missing_generated`
Expected: FAIL because we currently do not check generated artifact existence before writing approved copy.

- [ ] **Step 3: Write minimal implementation**

Add existence check for the generated artifact path before copying to the approved destination.

- [ ] **Step 4: Run test**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_project_store.py -q -k missing_generated`
Expected: PASS.

### Task 4: Run targeted regression suite and commit

**Files:**
- None (tests commands only)

- [ ] **Step 1: Run targeted tests**

Run: `/Users/zengxiangyi/HTML\ PPT\ V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_project_store.py tests/unit/test_cli.py -q`
Expected: PASS; ensures both negative and existing coverage succeed.

- [ ] **Step 2: Commit**

```
git add src/wllbe/cli.py src/wllbe/projects/store.py tests/unit/test_project_store.py tests/unit/test_cli.py docs/superpowers/plans/2026-03-25-outline-approval-harden-plan.md
git commit -m "fix: harden outline approval flow"
```
