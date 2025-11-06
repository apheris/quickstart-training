# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path

import numpy as np
from apheris_utils.data import download_dataset
from apheris_utils.data.primitives import get_settings
from apheris_utils.extras_nvflare.logging.gateway_log_sender import (
    GatewayLogSenderMixin,
    safe_error_catchall_decorator,
)
from nvflare.apis.dxo import DXO, DataKind, from_shareable
from nvflare.apis.executor import Executor
from nvflare.apis.fl_constant import FLContextKey, ReturnCode
from nvflare.apis.fl_context import FLContext
from nvflare.apis.shareable import Shareable, make_reply
from nvflare.apis.signal import Signal


# TODO: Delete this and replace all references with the actual model
class MockLogisticRegression:
    _coeffs: dict | None = None

    def fit(self, X, y):
        pass


class TrainingExecutor(GatewayLogSenderMixin, Executor):

    def __init__(self, cohorts: dict[str, str]):
        """
        Arguments are populated as an argument to the executor in the client configuration
        by the secure runtime, for more information, see`
        `secure_runtime/secure_runtime_service.py:create_template`.

        Args:
        TODO: document the above
        """
        super().__init__()

        self.cohorts = cohorts
        self.model = MockLogisticRegression()

        self.dataset_id: str | None = None

    def _download_dataset(self, fl_ctx: FLContext) -> Path:
        data_download_root = Path(fl_ctx.get_prop(FLContextKey.APP_ROOT)) / "datasets"

        # apheris_utils.data.download_dataset will download the dataset from the DAL
        # and return a dictionary with the dataset_id as the key and the path to the
        # local dataset as the value.
        data_dict = download_dataset(self.dataset_id, data_download_root)

        data_path = data_dict.get(self.dataset_id, None)

        if not data_path:
            raise RuntimeError(
                f"Failed to download dataset {self.dataset_id} from DAL. "
                "Please check the DAL settings and ensure the dataset is available."
            )
        return Path(data_path)

    @safe_error_catchall_decorator
    def execute(
        self,
        task_name: str,
        shareable: Shareable,
        fl_ctx: FLContext,
        abort_signal: Signal,
    ) -> Shareable:
        """
        This is the method that FLARE calls to run a task on the Gateway. The workflow
        calls tasks, and then we use conditionals in the execute method to determine
        what to do based on the task name.

        Note that this is wrapped with the `safe_error_catchall_decorator`, which will
        catch any unhandled exceptions and log them to the server without exposing the
        raw error message to the user.
        """

        # For this simple example, we assume there is only one dataset per site.
        dal_settings = get_settings()
        self.dataset_id = list(dal_settings.data.keys())[0]

        data_path = self._download_dataset(fl_ctx)

        # You can use the _send_to_server_log method to send log messages to the
        # server to be logged. This is useful for debugging and monitoring the
        # execution of your task. Messages will also be logged to the client logs.
        self._send_to_server_log(
            fl_ctx,
            f"Received task {task_name} for dataset {self.dataset_id}, with cohorts: "
            f"{self.cohorts}.",
            "INFO",
        )

        if abort_signal.triggered:
            return make_reply(ReturnCode.TASK_ABORTED)

        return self._train(
            input_shareable=shareable,
            fl_ctx=fl_ctx,
            dataset_path=data_path,
        )

    def _load_data_from_dataset(self, dataset_path: Path):
        """
        TODO: Replace the content of this method with the actual logic to load data from
        the dataset path. This is a placeholder method that should be
        replaced with actual data loading logic.

        e.g. you can use pandas to read a CSV file, or any other method
        to load the data from the dataset path. For now, we will just return
        some mock data for demonstration purposes.

        This will require some understanding of the dataset structure and how to
        extract the features and labels from it. The dataset_path will be the path
        to the dataset directory that was downloaded by the secure runtime.

        Example:
            df = pd.read_csv(dataset_path / "data.csv")
            X = df.drop(columns=["target"]).values
            y = df["target"].values
        """
        X = np.array([1, 2, 3, 4])
        y = np.array([2, 3, 4, 5])
        return X, y

    def _train(
        self, input_shareable: Shareable, fl_ctx: FLContext, dataset_path: Path
    ) -> Shareable:

        initial_coeffs = from_shareable(input_shareable).data

        X, y = self._load_data_from_dataset(dataset_path)

        # TODO: replace this mocked model with the actual sklearn model
        self.model._coeffs = initial_coeffs

        self.model.fit(X, y)

        # TODO: Extract model parameters
        params = self.model._coeffs

        dxo = DXO(DataKind.WEIGHTS, params)
        shareable = dxo.to_shareable()
        shareable.set_return_code(ReturnCode.OK)
        return shareable
