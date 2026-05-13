# Work Task Prompts

This file records the current small task prompt and later review result. The user-facing Chinese prompt is sent in chat for copy/paste; this file is kept as a compact review anchor.

Previous completed task:
- B-13 `update_schedule_fields` delegation: completed in commit `b2894b4 refactor: delegate schedule field updates`.

---

## 2026-05-14 B-14 delete_schedule delegation

Status: reviewed / pending commit
Commit: pending

### Task Scope

- Delegate only `DatabaseManager.delete_schedule(schedule_id)`.
- Allowed execution-window files:
  - `src/data/database.py`
  - `manage_instruction/Work_Log.md`
- `Work_Task_Prompts.md` is maintained by the advisor window, not the execution window.

### Forbidden Changes

- Do not modify `src/repositories/` unless `ScheduleRepository.delete_schedule` is missing; stop and explain first if so.
- Do not modify `src/ui/`.
- Do not modify `main.py`.
- Do not modify `src/theme/`.
- Do not modify `src/utils/signals.py`.
- Do not modify `requirements.txt`.
- Do not modify `Work_Snapshot.md`.
- Do not modify `Work_Task_Prompts.md` from the execution window.
- Do not leave any tracked `schedule.db` diff.
- Do not modify migration logic.
- Do not modify other Schedule write methods: `update_schedule_status`, `update_schedule_fields`, `toggle_pin_status`.
- Do not modify category methods.
- Do not modify repeat schedule logic: `add_schedule`, `update_schedule_with_repeat`, `_add_months`.
- Do not delete or modify existing real schedule samples.

### Expected Code Change

```python
return self.schedule_repository.delete_schedule(schedule_id)
```

### Required Validation

- Database import must pass.
- Missing id path should be printed but not hard-asserted.
- Create a temporary schedule through existing `db_manager.add_schedule(data)`.
- Temporary schedule title must start with `__tmp_b14_delete_`.
- Temporary schedule must use `repeat_rule='none'`.
- Find the temporary schedule by title.
- Delete only the temporary schedule.
- Confirm the temporary schedule id is no longer returned by `db_manager.get_all_schedules()`.
- Confirm `src/ui` has no diff.
- Confirm `schedule.db` has no tracked diff.

### Review Result

- `Work_Log.md` includes the B-14 task name, changed files, validation command/result, unfinished items, and risk notes.
- `git diff -- src/data/database.py` shows only the expected `delete_schedule` delegation.
- `git diff --name-only -- src/ui` has no output.
- `git diff --name-only -- schedule.db` has no output.
- Advisor reran validation successfully:
  - `db import ok`
  - missing id path was printed and not hard-asserted
  - temporary schedule was created with `repeat_rule='none'`
  - temporary schedule was found by title
  - `delete_schedule` returned `True`
  - temporary schedule id was no longer returned after deletion
