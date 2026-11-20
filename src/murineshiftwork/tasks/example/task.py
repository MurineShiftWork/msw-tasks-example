"""Example MSW task: demonstrates minimal hardware + settings access pattern.

Copy this file to start a new task. The run_task() function is the entry point
called by the MSW CLI. The Task class is a TaskRunner subclass that owns the
state machine loop.

See ``hook.py`` in this package for a worked example of a pre/post session
hook and how to register it from a setup or task YAML.
"""

import logging
import time

from murineshiftwork.logic.barcode import (
    BarcodeTTL,
    barcode_config_from_settings,
    inject_barcode_states,
)
from murineshiftwork.logic.task_process import TaskProcess, TaskRunner
from pybpodapi.protocol import Bpod
from pybpodapi.state_machine import StateMachine


class Task(TaskRunner):
    """Fixed-length trials with a barcode at the start and every ``barcode_interval_s``.

    The framework builds the Bpod connection and the session paths, and writes each
    trial passed to ``emit_trial``; the task only builds and runs state machines.
    """

    def run(self) -> None:
        # task.yaml values, with any CLI -ts overrides applied
        settings = self.input_kwargs.get("settings.task.patched", {})
        n_trials = int(settings.get("n_trials", 10))
        trial_duration = float(settings.get("trial_duration", 2.0))
        iti_duration = float(settings.get("iti_duration", 1.0))
        bnc_channel = getattr(
            self.bpod.OutputChannels, f"BNC{settings.get('barcode_channel', 1)}"
        )
        # barcode_bits / barcode_bit_duration_ms / ... keys, ttl-barcoder defaults
        barcoder = BarcodeTTL(barcode_config_from_settings(settings))
        trial_s = trial_duration + iti_duration
        barcode_interval_s = float(settings.get("barcode_interval_s", 30))
        barcode_every_n = max(1, round(barcode_interval_s / trial_s)) if trial_s else 1

        logging.info("Example task: starting %d trials", n_trials)
        trial_index = 0
        while self.continue_task and trial_index < n_trials:
            sma = StateMachine(bpod=self.bpod)
            barcode_value = barcode_wall_time = None
            if trial_index % barcode_every_n == 0:
                # barcode for ephys/video alignment, then the trial
                barcode_value, barcode_wall_time, timing = barcoder.prepare()
                sma = inject_barcode_states(
                    sma, timing, bnc_channel, last_state_name="trial_start"
                )
            sma.add_state(
                state_name="trial_start",
                state_timer=trial_duration,
                state_change_conditions={Bpod.Events.Tup: "iti"},
                output_actions=[],
            )
            sma.add_state(
                state_name="iti",
                state_timer=iti_duration,
                state_change_conditions={Bpod.Events.Tup: "exit"},
                output_actions=[],
            )

            self.bpod.send_state_machine(sma)
            if not self.bpod.run_state_machine(sma):
                logging.warning("No data returned on trial %d: stopping", trial_index)
                break

            trial = self.bpod.session.current_trial.export()
            trial["info"] = {
                "trial_index": trial_index,
                "barcode_value": barcode_value,
                "barcode_wall_time": barcode_wall_time,
            }
            self.emit_trial(trial)  # the framework writes df.jsonl
            logging.info("Trial %d/%d complete", trial_index + 1, n_trials)
            trial_index += 1

        logging.info("Example task: done.")


def run_task(**kwargs):
    """Entry point called by the MSW CLI (``msw run example``)."""
    with TaskProcess(**kwargs) as tp:
        while tp.is_running():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                tp.stop_task()
