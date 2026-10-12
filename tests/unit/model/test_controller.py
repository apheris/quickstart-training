# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from unittest.mock import MagicMock, patch

import pytest
from nvflare.apis.fl_context import FLContext
from nvflare.app_common.app_constant import AppConstants
from nvflare.app_common.app_event_type import AppEventType

from logistic_regression_quickstart.model.controller import TrainingController


@pytest.fixture
def controller():
    return TrainingController(
        min_clients=1,
        num_rounds=2,
        start_round=0,
        wait_time_after_min_received=0,
        aggregator_id="aggregator",
        persistor_id="",
        shareable_generator_id="shareable_generator",
        train_task_name="train",
        train_timeout=0,
    )


def test_controller_is_scatter_and_gather_subclass():
    from nvflare.app_common.workflows.scatter_and_gather import ScatterAndGather

    assert issubclass(TrainingController, ScatterAndGather)


def test_hook_methods_exist(controller):
    assert callable(controller.on_initialize)
    assert callable(controller.on_training_started)
    assert callable(controller.on_round_started)
    assert callable(controller.on_before_aggregation)
    assert callable(controller.on_after_aggregation)
    assert callable(controller.on_round_done)
    assert callable(controller.on_finalize)


def test_handle_event_dispatches_to_hooks(controller, fl_ctx: FLContext):
    controller._current_round = 0

    for hook_name, event_type in [
        ("on_training_started", AppEventType.TRAINING_STARTED),
        ("on_round_started", AppEventType.ROUND_STARTED),
        ("on_before_aggregation", AppEventType.BEFORE_AGGREGATION),
        ("on_after_aggregation", AppEventType.AFTER_AGGREGATION),
        ("on_round_done", AppEventType.ROUND_DONE),
    ]:
        mock_hook = MagicMock()
        setattr(controller, hook_name, mock_hook)

        with patch.object(
            controller.__class__.__bases__[0], "handle_event", return_value=None
        ):
            controller.handle_event(event_type, fl_ctx)

        mock_hook.assert_called_once()


def test_on_training_done_called_on_clean_finish(controller, fl_ctx: FLContext):
    abort_signal = MagicMock(triggered=False)
    controller._phase = AppConstants.PHASE_FINISHED
    mock_done = MagicMock()
    controller.on_training_done = mock_done

    with patch.object(controller.__class__.__bases__[0], "control_flow"):
        controller.control_flow(abort_signal, fl_ctx)

    mock_done.assert_called_once_with(fl_ctx)


def test_on_training_done_not_called_on_abort(controller, fl_ctx: FLContext):
    abort_signal = MagicMock(triggered=True)
    controller._phase = AppConstants.PHASE_FINISHED
    mock_done = MagicMock()
    controller.on_training_done = mock_done

    with patch.object(controller.__class__.__bases__[0], "control_flow"):
        controller.control_flow(abort_signal, fl_ctx)

    mock_done.assert_not_called()


def test_subclass_hooks_are_called(fl_ctx: FLContext):
    """Verify that a subclass can override hooks and they will be called."""

    class RecordingController(TrainingController):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.calls = []

        def on_round_started(self, current_round, fl_ctx):
            self.calls.append(("on_round_started", current_round))

        def on_round_done(self, current_round, fl_ctx):
            self.calls.append(("on_round_done", current_round))

    ctrl = RecordingController(
        min_clients=1,
        num_rounds=2,
        start_round=0,
        wait_time_after_min_received=0,
        train_task_name="train",
        train_timeout=0,
    )
    ctrl._current_round = 1

    with patch.object(TrainingController.__bases__[0], "handle_event", return_value=None):
        ctrl.handle_event(AppEventType.ROUND_STARTED, fl_ctx)
        ctrl.handle_event(AppEventType.ROUND_DONE, fl_ctx)

    assert ctrl.calls == [("on_round_started", 1), ("on_round_done", 1)]
