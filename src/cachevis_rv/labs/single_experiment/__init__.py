"""Public single-experiment runner API."""

from .runner import (
    DEFAULT_START_ADDRESS,
    SOFTWARE_NAME,
    SOFTWARE_VERSION,
    build_trace,
    make_single_experiment_conclusion,
    run_single_experiment,
)
from .controller import SingleExperimentController
from .view_model import SingleExperimentViewModel

__all__ = [
    "SOFTWARE_NAME",
    "SOFTWARE_VERSION",
    "DEFAULT_START_ADDRESS",
    "build_trace",
    "run_single_experiment",
    "make_single_experiment_conclusion",
    "SingleExperimentController",
    "SingleExperimentViewModel",
    "SingleExperimentWidget",
]


def __getattr__(name: str):
    if name == "SingleExperimentWidget":
        from .widget import SingleExperimentWidget

        return SingleExperimentWidget
    raise AttributeError(name)
