import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional


class UploaderService:
    def __init__(
        self,
        data_dir: str,
        remote_name: str,
        upload_interval_sec: int,
        logger,
        enabled: bool = False,
    ):
        self.data_dir = Path(data_dir)
        self.remote_name = remote_name
        self.upload_interval_sec = upload_interval_sec
        self.logger = logger
        self.enabled = enabled
        self.last_upload_time = 0.0

    def should_upload(self) -> bool:
        if not self.enabled:
            return False

        now = time.time()
        return (now - self.last_upload_time) >= self.upload_interval_sec

    def upload_once(self) -> bool:
        """
        Upload local raw data directory to the configured rclone remote.
        Returns True on success, False on failure.
        """
        if not self.enabled:
            return False

        if not self.data_dir.exists():
            self.logger.warning(f"Upload skipped: data directory does not exist: {self.data_dir}")
            return False

        if shutil.which("rclone") is None:
            self.logger.error("Upload failed: rclone is not installed or not in PATH")
            return False

        remote_target = f"{self.remote_name}:Refrigeration-Sensor-Hub"

        command = [
            "rclone",
            "copy",
            str(self.data_dir),
            remote_target,
            "--create-empty-src-dirs",
        ]

        self.logger.info(f"Starting upload: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )

            if result.returncode == 0:
                self.last_upload_time = time.time()
                self.logger.info("Upload completed successfully")
                if result.stdout.strip():
                    self.logger.info(f"rclone stdout: {result.stdout.strip()}")
                return True

            self.logger.error(f"Upload failed with code {result.returncode}")
            if result.stdout.strip():
                self.logger.error(f"rclone stdout: {result.stdout.strip()}")
            if result.stderr.strip():
                self.logger.error(f"rclone stderr: {result.stderr.strip()}")
            return False

        except subprocess.TimeoutExpired:
            self.logger.error("Upload failed: rclone command timed out")
            return False
        except Exception as e:
            self.logger.exception(f"Upload failed with unexpected error: {e}")
            return False
