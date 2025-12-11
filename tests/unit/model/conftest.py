# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from nvflare.apis.client import Client
from nvflare.apis.fl_component import FLComponent
from nvflare.apis.fl_constant import FLContextKey, ReservedKey
from nvflare.apis.fl_context import FLContext
from nvflare.apis.workspace import Workspace


# Define some session fixtures for different paths we might want to reference in our tests
@pytest.fixture(scope="session")
def tmp_path_app_root(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("app_path")


@pytest.fixture(scope="session")
def tmp_path_dataset_root(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("app_data")


@pytest.fixture
def aph_data() -> dict:
    return {
        "medical-decathlon-task004-hippocampus-a-files_gateway-1_org-1": (
            "s3://apheris-tutorials-data/nnunetv2/dataset004_hippocampus/a/"
            "Dataset004_Hippocampus_A/"
        ),
        "whas1_gateway-1_org-1": "s3://apheris-tutorials-data/whas/worcester/data.csv",
    }


@pytest.fixture
def monkeypatch_dal_env(aph_data, tmp_path_dataset_root):
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("APH_DATA", json.dumps(aph_data))
        mp.setenv("APH_DAL_TOKEN", "notarealtoken")
        mp.setenv("APH_API_DAL_URL", "http://not-a-url")

        yield mp


@pytest.fixture
def monkeypatch_dal_env_local(aph_data, tmp_path_dataset_root):
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("APH_DATA", json.dumps(aph_data))
        yield mp


class FakeEngine:
    def __init__(self, num_clients: int) -> None:
        self.num_clients = num_clients
        self._clients = [
            Client(f"test_client{i}", str(uuid4())) for i in range(self.num_clients)
        ]

        self._workspace_mock = MagicMock()
        self._component_mock = MagicMock()

        self.components: dict = {}

    def get_component(self, c_id: str) -> FLComponent:
        if not self.components:
            return self._component_mock
        return self.components[c_id]

    def get_clients(self) -> List[Client]:
        return self._clients

    def get_workspace(self) -> Workspace:
        return self._workspace_mock

    def __getattr__(self, name) -> MagicMock:
        return MagicMock()


@pytest.fixture
def mock_path() -> Path:
    return Path("path/to/a/checkpoint")


@pytest.fixture
def fl_ctx(mocker, mock_path: Path, tmp_path_app_root: Path) -> FLContext:
    f = FLContext()
    f.set_prop(ReservedKey.IDENTITY_NAME, "test_client1")
    f.set_prop(ReservedKey.RUN_NUM, 4)
    f.set_prop(FLContextKey.APP_ROOT, tmp_path_app_root)

    eng = FakeEngine(2)
    eng.get_workspace().get_run_dir.return_value = str(mock_path)

    f.put(key=ReservedKey.ENGINE, value=eng, private=True, sticky=False)

    return f
