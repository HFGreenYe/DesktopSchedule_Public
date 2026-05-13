# Work Task Prompts

This file records the current small task prompt and later review result. The user-facing Chinese prompt is sent in chat for copy/paste; this file is kept as a compact review anchor.

Previous completed task:
- B-10 `hard_delete_category` delegation: completed in commit `64f0427 refactor: delegate category hard delete`.

---

## 2026-05-13 B-11 update_schedule_status delegation

Status: reviewed / pending commit
Commit: pending

### Task Scope

- Delegate only `DatabaseManager.update_schedule_status(schedule_id, new_status)`.
- Allowed execution-window files:
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- `Work_Task_Prompts.md` is maintained by the advisor window, not the execution window.

### Forbidden Changes

- Do not modify `src/repositories/` unless `ScheduleRepository.update_schedule_status` is missing; stop and explain first if so.
- Do not modify `src/ui/`.
- Do not modify `main.py`.
- Do not modify `src/theme/`.
- Do not modify `src/utils/signals.py`.
- Do not modify `requirements.txt`.
- Do not modify `Work_Snapshot.md`.
- Do not modify `Work_Task_Prompts.md` from the execution window.
- Do not leave any tracked `schedule.db` diff.
- Do not modify migration logic.
- Do not modify other Schedule write methods: `delete_schedule`, `update_schedule_fields`, `toggle_pin_status`.
- Do not modify category methods.
- Do not modify repeat schedule logic: `add_schedule`, `update_schedule_with_repeat`, `_add_months`.

### Expected Code Change

```python
return self.schedule_repository.update_schedule_status(schedule_id, new_status)
```

### Required Validation

- Database import must pass.
- Missing id path should be printed but not hard-asserted.
- If an existing schedule sample exists, write the original status back to the same schedule and verify it remains unchanged.
- If no sample exists, do not create complex schedule data; record that real write validation was skipped.
- Confirm `src/ui` has no diff.
- Confirm `schedule.db` has no tracked diff.

### Review Result

- `Work_Log.md` includes the B-11 task name, changed files, validation command/result, unfinished items, and risk notes.
- `git diff -- src/data/database.py` shows only the expected `update_schedule_status` delegation.
- `git diff --name-only -- src/ui` has no output.
- `git diff --name-only -- schedule.db` has no output.
- Advisor reran validation successfully:
  - `db import ok`
  - missing id path was printed and not hard-asserted
  - existing sample schedule was updated with its original status
  - verification confirmed the status remained unchanged
