import json
from pathlib import Path
from typing import Dict, Any

from utils.time_utils import utc_date_string


class JsonLineLogger:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_daily_log_path(self) -> Path:
        date_str = utc_date_string()
        return self.data_dir / f"log_{date_str}.json"

    def write_record(self, record: Dict[str, Any]) -> None:
        log_path = self.get_daily_log_path()

        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
