"""Example MSW session hook: the minimal pre/post hook pattern.

A hook runs around a task session without being part of the task's state
machine. Use one for cross-cutting concerns: weigh the animal before a session,
check the environment, send a notification, or export/QC data afterwards.

Two call points (defined by ``murineshiftwork.hooks.TaskHook``):

  pre_run(ctx)  - after hardware connects, before the task starts. May mutate
                  ``ctx.task_settings`` (the task sees the change) and may stash
                  state in ``ctx.output`` for the post hook to read.
  post_run(ctx) - after the task ends, before hardware disconnects. May read
                  ``ctx.output`` and the written session files.

Set ``fatal = True`` to ABORT the session when the hook raises; otherwise a
raising hook logs a warning and the session continues.

Registering a hook (by dotted path) - either location works:

  # setup YAML (applies to every task run on this rig):
  hooks:
    pre_task:  ["murineshiftwork.tasks.example.hook.ExampleHook"]
    post_task: ["murineshiftwork.tasks.example.hook.ExampleHook"]

  # or task.yaml (applies to this task only):
  HOOKS_PRE_TASK:  ["murineshiftwork.tasks.example.hook.ExampleHook"]
  HOOKS_POST_TASK: ["murineshiftwork.tasks.example.hook.ExampleHook"]

Setup-level and task-level hooks both run (setup first, then task).
"""

from __future__ import annotations

import logging

from murineshiftwork.hooks import HookContext, TaskHook

log = logging.getLogger(__name__)


class ExampleHook(TaskHook):
    """Demonstration hook: logs around the session and shares state pre -> post.

    Copy this and replace the bodies with real work. Keep pre_run fast: it runs
    while hardware is connected and before the first trial.
    """

    # If the hook's work is required for a valid session, set this True so a
    # failure aborts the session instead of being logged and skipped.
    fatal = False

    def pre_run(self, ctx: HookContext) -> None:
        """Runs once before the task starts."""
        log.info(
            "ExampleHook.pre_run: subject=%s task=%s",
            ctx.subject,
            ctx.task_name,
        )
        # A pre hook can adjust settings the task will read, e.g.:
        #   ctx.task_settings["n_trials"] = 5
        # and stash state for the post hook to pick up:
        ctx.output["example_pre_ran"] = True

    def post_run(self, ctx: HookContext) -> None:
        """Runs once after the task ends."""
        log.info(
            "ExampleHook.post_run: subject=%s pre_ran=%s session=%s",
            ctx.subject,
            ctx.output.get("example_pre_ran", False),
            ctx.session_paths.get("session_folder", ""),
        )
