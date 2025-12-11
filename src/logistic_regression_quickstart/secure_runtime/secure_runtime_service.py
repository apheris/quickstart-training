# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from pathlib import Path
from typing import Optional

from .loaders import load_client_config, load_server_config
from .payload import LogisticRegressionPayload


def parse(body: str) -> LogisticRegressionPayload:
    """
    Maps input body into a structured payload.

    Raises ValueError if it can not be parsed.
    """
    try:
        payload = LogisticRegressionPayload.model_validate_json(body)
    except Exception as exc:
        raise ValueError("Failed to parse the input payload.") from exc

    return payload


def validate(payload: dict) -> None:
    """
    Validates the input payload (optional)

    Raises ValueError
    """
    # Nothing to do here, the payload is already validated by the Pydantic model
    pass


def template(
    payload: LogisticRegressionPayload,
    _dataset2gw: Optional[dict] = None,
    *,
    template_folder: Optional[Path] = None,
) -> dict:

    if _dataset2gw is None:
        raise ValueError("Missing dataset2gw mapping.")

    num_clients = len(_dataset2gw.values())

    return {
        "app/config/config_fed_client.json": load_client_config(payload),
        "app/config/config_fed_server.json": load_server_config(payload, num_clients),
        "meta.json": {
            "name": "simple",
            "resource_spec": {},
            "min_clients": num_clients,
            "deploy_map": {"app": ["@ALL"]},
        },
    }
