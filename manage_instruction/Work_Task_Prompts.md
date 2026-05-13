# Work Task Prompts

This file records the current small task prompt and review result. The full user-facing Chinese prompt is sent in chat for easy copy/paste; this file is kept as a compact review anchor to avoid encoding churn.

---

## 2026-05-13 B-8 add_category delegation

Status: reviewed / pending commit
Commit: pending

### Task Scope

- Delegate only `DatabaseManager.add_category(name, color="#0cc0df", list_type="schedule")`.
- Allowed files:
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- Do not modify:
  - `src/repositories/`
  - `src/ui/`
  - `main.py`
  - `src/theme/`
  - `src/utils/signals.py`
  - `requirements.txt`
  - `Work_Snapshot.md`
  - migration logic
  - other write/status methods

### Expected Code Change

```python
return self.category_repository.add_category(name, color, list_type)
```

### Required Validation

- Create a temporary unique category through `db_manager.add_category(...)`.
- Read it back through `db_manager.get_category(...)`.
- Clean it up through existing `db_manager.hard_delete_category(...)`.
- Confirm cleanup returns `True`.
- Confirm reading after cleanup returns `None`.
- Confirm `src/ui` has no diff.
- Confirm no `schedule.db` diff is tracked.

### Review Result

- `Work_Log.md` includes the B-8 task name, changed files, validation command/result, unfinished items, and risk notes.
- `git diff -- src/data/database.py` shows only the expected `add_category` delegation.
- `git diff --name-only -- src/ui` has no output.
- `git diff --name-only -- schedule.db` has no output.
- Advisor reran validation successfully:
  - `db import ok`
  - temporary category was created
  - category was read back by id
  - cleanup returned `True`
  - reading after cleanup returned `None`
