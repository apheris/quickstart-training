# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

import json

import pytest

from logistic_regression_quickstart.secure_runtime.secure_runtime_service import (
    LogisticRegressionPayload,
    parse,
    template,
    validate,
)


def test_parse_valid_json():
    """Test parse function with valid JSON input for task 'list_files'."""
    valid_body = '{"task_id": "train", "cohorts": {}}'
    result = parse(valid_body)
    assert isinstance(result, LogisticRegressionPayload)
    assert result.task_id == "train"


def test_parse_valid_json_with_preprocess():
    """Test parse function with valid JSON input for task 'preprocess'."""
    valid_payload_dict = {"task_id": "train", "cohorts": {}}
    result = parse(json.dumps(valid_payload_dict))
    assert isinstance(result, LogisticRegressionPayload)
    assert result.task_id == "train"


def test_validate_no_action():
    """Test validate function which currently does nothing."""
    validate({"task_id": "list_files", "dataset_id": "dataset_123"})  # Placeholder check


def test_template_generation_no_dsmap():
    payload = LogisticRegressionPayload(task_id="train", cohorts={})
    with pytest.raises(ValueError, match="Missing dataset2gw mapping."):
        template(payload, _dataset2gw=None)
