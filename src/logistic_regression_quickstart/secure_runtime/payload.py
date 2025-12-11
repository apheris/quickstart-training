# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

from typing import Literal

from pydantic import BaseModel, Field

TaskID = Literal["train"]


# TODO: Update this with the relevant fields for the Logistic Regression Payload
class LogisticRegressionPayload(BaseModel):
    task_id: TaskID
    cohorts: dict[str, str] = Field(default_factory=dict)
    num_rounds: int = 2
