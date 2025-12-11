# Copyright (c) 2024 apheris AI GmbH.  All rights reserved.

import json
import logging
from pathlib import Path
from typing import Dict


def write_job_configs(job_root_path: Path, configs: Dict[str, Dict]):
    for config_path, content in configs.items():
        output_path = job_root_path / config_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(content, f, indent=2)

        logging.info(f"Wrote {config_path} to {output_path}")


__all__ = [
    "write_job_configs",
]
