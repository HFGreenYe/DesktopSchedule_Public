# Work Task Prompts

This file records the current small task prompt and later review result. The user-facing Chinese prompt is sent in chat for copy/paste; this file is kept as a compact review anchor.

Previous completed task:
- B-9 `soft_delete_category` delegation: completed in commit `71cdcbf refactor: delegate category soft delete`.

---

## 2026-05-13 B-10 hard_delete_category delegation

Status: reviewed / pending commit
Commit: pending

### Task Scope

- Delegate only `DatabaseManager.hard_delete_category(cat_id)`.
- Allowed execution-window files:
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- `Work_Task_Prompts.md` is maintained by the advisor window, not the execution window.

### Forbidden Changes

- Do not modify `src/repositories/` unless `CategoryRepository.hard_delete_category` is missing; stop and explain first if so.
- Do not modify `src/ui/`.
- Do not modify `main.py`.
- Do not modify `src/theme/`.
- Do not modify `src/utils/signals.py`.
- Do not modify `requirements.txt`.
- Do not modify `Work_Snapshot.md`.
- Do not modify `Work_Task_Prompts.md` from the execution window.
- Do not leave any tracked `schedule.db` diff.
- Do not modify migration logic.
- Do not modify other write/status methods.
- Do not modify Schedule-related methods.

### Expected Code Change

```python
return self.category_repository.hard_delete_category(cat_id)
```

### Required Validation

- Create a temporary unique category through `db_manager.add_category(...)`.
- Confirm it exists through `db_manager.get_category(cat_id)`.
- Call `db_manager.hard_delete_category(cat_id)`.
- Confirm it returns `True`.
- Confirm `db_manager.get_category(cat_id)` returns `None` after deletion.
- Confirm `src/ui` has no diff.
- Confirm `schedule.db` has no tracked diff.

### Review Result

- `Work_Log.md` includes the B-10 task name, changed files, validation command/result, unfinished items, and risk notes.
- `git diff -- src/data/database.py` shows only the expected `hard_delete_category` delegation.
- `git diff --name-only -- src/ui` has no output.
- `git diff --name-only -- schedule.db` has no output.
- Advisor reran validation successfully:
  - `db import ok`
  - temporary category was created
  - category existed before deletion
  - `hard_delete_category` returned `True`
  - reading after deletion returned `None`
