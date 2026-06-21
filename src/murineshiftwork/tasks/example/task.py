"""Example MSW task: demonstrates minimal hardware + settings access pattern.

Copy this file to start a new task. The run_task() function is the entry point
called by the MSW CLI. The Task class is a TaskRunner subclass that owns the
state machine loop.

See ``hook.py`` in this package for a worked example of a pre/post session
hook and how to register it from a setup or task YAML.
"""

import logging
import time

import numpy as np
from murineshiftwork.hardware.bpod import BpodFactory
from murineshiftwork.logic.barcode import (
    BarcodeTTL,
    barcode_config_from_settings,
    inject_barcode_states,
)
from murineshiftwork.logic.io import save_trial_data
from murineshiftwork.logic.task_process import TaskRunner
from murineshiftwork.namespace import msw_file
from pybpodapi.protocol import Bpod, StateMachine


class Task(TaskRunner):
    def __init__(self, bpod: Bpod, **settings):
        super().__init__(bpod=bpod, **settings)

        # Access task settings (from task.yaml defaults, overridden by CLI -ts flags).
        self.n_trials = int(settings.get("n_trials", 10))
        self.trial_duration = float(settings.get("trial_duration", 2.0))
        self.iti_duration = float(settings.get("iti_duration", 1.0))

        # Print all settings so the user can verify what is active.
        print("\n--- Example Task Settings ---")
        for k, v in settings.items():
            print(f"  {k}: {v}")
        print("----------------------------\n")

        # Barcode TTL for ephys alignment (optional but recommended).
        barcode_cfg = barcode_config_from_settings(settings)
        self.barcode = BarcodeTTL(**barcode_cfg) if barcode_cfg else None

    def run(self):
        logging.info("Example task: starting %d trials", self.n_trials)

        for trial_n in range(self.n_trials):
            if not self._running:
                break

            sma = StateMachine(self.bpod)

            # Inject barcode at session start and every ~30 s.
            if self.barcode and (trial_n == 0 or trial_n % 30 == 0):
                inject_barcode_states(sma, self.barcode, next_state="trial_start")
            else:
                sma.add_state(
                    state_name="trial_start",
                    state_timer=self.trial_duration,
                    state_change_conditions={"Tup": "iti"},
                    output_actions=[],
                )

            sma.add_state(
                state_name="iti",
                state_timer=self.iti_duration,
                state_change_conditions={"Tup": "exit"},
                output_actions=[],
            )
            sma.add_state(
                state_name="exit",
                state_timer=0,
                state_change_conditions={},
                output_actions=[],
            )

            self.bpod.send_state_machine(sma)
            self.bpod.run_state_machine(sma)

            trial_data = {
                "trial": trial_n,
                "trial_duration": self.trial_duration,
                "iti_duration": self.iti_duration,
                "timestamp": time.time(),
                "dummy_value": float(np.random.rand()),
            }
            save_trial_data(
                data=trial_data,
                file_path=msw_file(self.session_paths["session_file_path"], "df.jsonl"),
            )
            logging.info(
                "Trial %d/%d complete. dummy_value=%.4f",
                trial_n + 1,
                self.n_trials,
                trial_data["dummy_value"],
            )

        logging.info("Example task: done.")


def run_task(bpod_serial_port: str, data_path: str, **settings):
    """Entry point called by the MSW CLI (msw run example)."""
    bpod = BpodFactory(serial_port=bpod_serial_port).connect()
    try:
        task = Task(bpod=bpod, data_path=data_path, **settings)
        task.start()
        task.join()
    finally:
        bpod.close()
