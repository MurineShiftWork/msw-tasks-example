"""Example hook: pre/post run and pre -> post state sharing."""

from __future__ import annotations

from murineshiftwork.hooks import HookContext

from murineshiftwork.tasks.example.hook import ExampleHook


def _ctx() -> HookContext:
    return HookContext(
        subject="s1",
        task_name="example",
        task_settings={},
        session_paths={"session_folder": "/tmp/s1"},
    )


def test_pre_run_stashes_state():
    ctx = _ctx()
    ExampleHook().pre_run(ctx)
    assert ctx.output["example_pre_ran"] is True


def test_post_run_reads_pre_state():
    ctx = _ctx()
    hook = ExampleHook()
    hook.pre_run(ctx)
    hook.post_run(ctx)  # reads the stashed flag, must not raise
    assert ctx.output["example_pre_ran"] is True


def test_not_fatal_by_default():
    assert ExampleHook.fatal is False
