"""The example task runs on the simulated Bpod and emits one record per trial."""

from __future__ import annotations

from murineshiftwork.hardware.bpod.sim import SimBpod

from murineshiftwork.tasks.example.task import Task


class _Writer:
    def __init__(self) -> None:
        self.trials: list[dict] = []

    def write_trial(self, trial: dict) -> None:
        self.trials.append(trial)


def _run(**settings) -> list[dict]:
    bpod = SimBpod()
    bpod.open()
    writer = _Writer()
    Task(bpod=bpod, trial_writer=writer, **{"settings.task.patched": settings}).run()
    return writer.trials


def test_one_record_per_trial():
    trials = _run(n_trials=4, trial_duration=0.0, iti_duration=0.0)
    assert [t["info"]["trial_index"] for t in trials] == [0, 1, 2, 3]


def test_barcode_on_the_first_trial_and_every_interval():
    trials = _run(
        n_trials=5, trial_duration=1.0, iti_duration=1.0, barcode_interval_s=4
    )
    sent = [t["info"]["barcode_value"] is not None for t in trials]
    assert sent == [True, False, True, False, True]
