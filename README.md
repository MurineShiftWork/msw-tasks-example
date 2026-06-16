# msw-tasks-example

Minimal example task for [Murine Shift Work](https://github.com/MurineShiftWork/msw-core).

Demonstrates the standard task structure: `Task(TaskRunner)` subclass, settings access from `task.yaml`, TTL barcode injection, and per-trial data saving via `save_trial_data()`.

## Install

```bash
git clone https://github.com/MurineShiftWork/msw-tasks-example
pip install -e msw-tasks-example
```

## Run

```bash
msw run example --subject test_subject --setup /path/to/setup.yaml
```

## Task structure

```
src/murineshiftwork/tasks/example/
    task.py      # Task class + run_task() entry point
    task.yaml    # Default settings (overridden by -ts KEY=VALUE on CLI)
```

## Writing a new task

1. Copy `src/murineshiftwork/tasks/example/` to a new directory.
2. Rename the entry point in `pyproject.toml`.
3. Implement your state machine in `Task.run()`.
