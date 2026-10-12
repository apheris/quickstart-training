# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path
from uuid import UUID

from apheris_utils.artifacts import Artifact, ArtifactType
from nvflare.apis.fl_context import FLContext
from nvflare.apis.signal import Signal
from nvflare.app_common.app_constant import AppConstants
from nvflare.app_common.app_event_type import AppEventType
from nvflare.app_common.workflows.scatter_and_gather import ScatterAndGather


class TrainingController(ScatterAndGather):
    """
    Extends ScatterAndGather with hook methods for orchestrator-side customization.

    Override any of the hook methods below to inject logic at specific points in
    the federated training lifecycle without rewriting the workflow loop:

        on_initialize(fl_ctx)
            After ScatterAndGather resolves components and loads the global model.

        on_training_started(fl_ctx)
            When the training phase begins, before round 0.

        on_round_started(current_round, fl_ctx)
            At the start of each round, before the task is scattered to clients.

        on_before_aggregation(current_round, fl_ctx)
            After all client responses are collected, before aggregation runs.

        on_after_aggregation(current_round, fl_ctx)
            After aggregation, before the global model is updated.

        on_round_done(current_round, fl_ctx)
            At the end of each round, after the global model is updated.

        on_training_done(fl_ctx)
            After all rounds complete successfully (not called on abort).

        on_finalize(fl_ctx)
            When the controller shuts down (always called, even on abort).

    Example::

        class MyController(TrainingController):
            def on_training_done(self, fl_ctx: FLContext) -> None:
                self.log_info(fl_ctx, "All rounds finished — exporting model.")
    """

    def start_controller(self, fl_ctx: FLContext) -> None:
        super().start_controller(fl_ctx)
        self.on_initialize(fl_ctx)

    def stop_controller(self, fl_ctx: FLContext) -> None:
        super().stop_controller(fl_ctx)
        self.on_finalize(fl_ctx)

    def control_flow(self, abort_signal: Signal, fl_ctx: FLContext) -> None:
        super().control_flow(abort_signal, fl_ctx)
        if self._phase == AppConstants.PHASE_FINISHED and not abort_signal.triggered:
            self.on_training_done(fl_ctx)

    def handle_event(self, event_type: str, fl_ctx: FLContext) -> None:
        super().handle_event(event_type, fl_ctx)
        if event_type == AppEventType.TRAINING_STARTED:
            self.on_training_started(fl_ctx)
        elif event_type == AppEventType.ROUND_STARTED:
            self.on_round_started(self._current_round, fl_ctx)
        elif event_type == AppEventType.BEFORE_AGGREGATION:
            self.on_before_aggregation(self._current_round, fl_ctx)
        elif event_type == AppEventType.AFTER_AGGREGATION:
            self.on_after_aggregation(self._current_round, fl_ctx)
        elif event_type == AppEventType.ROUND_DONE:
            self.on_round_done(self._current_round, fl_ctx)

    # -------------------------------------------------------------------------
    # Hook methods — override in a subclass to add orchestrator logic
    # -------------------------------------------------------------------------

    def on_initialize(self, fl_ctx: FLContext) -> None:
        """Called after components are resolved and the global model is loaded."""
        pass

    def on_training_started(self, fl_ctx: FLContext) -> None:
        """Called when training begins, before the first round."""
        pass

    def on_round_started(self, current_round: int, fl_ctx: FLContext) -> None:
        """Called at the start of each round, before scatter."""
        pass

    def on_before_aggregation(self, current_round: int, fl_ctx: FLContext) -> None:
        """Called after all client responses are collected, before aggregation."""
        pass

    def on_after_aggregation(self, current_round: int, fl_ctx: FLContext) -> None:
        """Called after aggregation, before the global model is updated."""
        pass

    def on_round_done(self, current_round: int, fl_ctx: FLContext) -> None:
        """Called at the end of each round, after the global model is updated."""
        pass

    def on_training_done(self, fl_ctx: FLContext) -> None:
        """Called once after all rounds complete successfully. Not called on abort."""
        job_id = fl_ctx.get_job_id()
        workspace = fl_ctx.get_workspace()
        model_path = Path(workspace.get_result_root(job_id)) / "models" / "server.npy"

        artifact = Artifact(
            job_id=UUID(job_id),
            type=ArtifactType.CHECKPOINT,
            name="FCP-Demo",
            metadata={},
        )
        self.log_info(fl_ctx, f"Saving artifact: {artifact}")
        artifact.add_file(local_path=model_path)
        self.log_info(fl_ctx, "saving artifact")
        artifact.save()
        self.log_info(fl_ctx, "artifact saved.")
        artifact_id = artifact.id
        self.log_info(fl_ctx, f"artifact_id: {artifact_id}")
        self.log_info(fl_ctx, f"job_id: {job_id}")

    def on_finalize(self, fl_ctx: FLContext) -> None:
        """Called when the workflow shuts down (always, even on abort)."""
        pass
