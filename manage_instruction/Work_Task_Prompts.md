# Work Task Prompts

This file records the current small task prompt and later review result. The user-facing Chinese prompt is sent in chat for copy/paste; this file is kept as a compact review anchor.

Previous completed task:
- B-14 `delete_schedule` delegation: completed in commit `1079352 refactor: delegate schedule deletion`.

---

## 2026-05-14 B-15 round-B technical validation

Status: reviewed / pending commit
Commit: pending

### Task Scope

- Validate round B as a whole.
- No architecture/code changes.
- Allowed execution-window files:
  - `manage_instruction/Work_Log.md`
- `Work_Task_Prompts.md` is maintained by the advisor window, not the execution window.

### Required Validation

- Repository imports.
- `db_manager` import.
- Delegated read paths.
- Delegated category write paths with temporary category data.
- Delegated schedule write paths with write-back/or temporary schedule data.
- GUI smoke test, or `main` import fallback if GUI cannot run.
- Confirm `src/ui` has no diff.
- Confirm `schedule.db` has no tracked diff.
- Confirm final diff only contains allowed management/log files.

### Review Result

- `Work_Log.md` includes the B-15 validation summary, modified files, command/result summaries, GUI smoke result, diff checks, unfinished items, and risk notes.
- Advisor reran Repository/db_manager/read-path validation successfully.
- Advisor reran category temporary write-path validation successfully.
- Advisor reran schedule write-back and temporary delete validation successfully.
- Advisor reran GUI smoke test successfully:
  - `gui smoke ok`
  - `libpng warning: tRNS: invalid with alpha channel` appeared, but it did not block startup.
- `git diff --name-only -- src/ui` has no output.
- `git diff --name-only -- schedule.db` has no output.
- Final diff contains only:
  - `manage_instruction/Work_Log.md`
  - `manage_instruction/Work_Task_Prompts.md`
