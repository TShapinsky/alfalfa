import shutil
import sys
from os import PathLike
from pathlib import Path
from typing import Dict, List

from alfalfa_worker.lib.logger_mixins import LoggerMixinBase
from alfalfa_worker.lib.point import Point
from alfalfa_worker.lib.run import Run
from alfalfa_worker.lib.run_manager import RunManager


class MockRunManager(RunManager, LoggerMixinBase):
    runs: Dict[str, Run] = {}

    def __init__(self, run_dir: Path, s3_dir: Path):
        self.run_dir = run_dir
        self.s3_dir = s3_dir
        if not self.s3_dir.exists():
            self.s3_dir.mkdir()
        (self.s3_dir / 'run').mkdir()
        (self.s3_dir / 'uploads').mkdir()
        self.tmp_dir = run_dir / 'tmp'
        if not self.tmp_dir.exists():
            self.tmp_dir.mkdir()
        LoggerMixinBase.__init__(self, "MockRunManager")

    def s3_download(self, key: str, file_path: PathLike):
        src = self.s3_dir / key
        shutil.copy(src, file_path)

    def s3_upload(self, file_path: PathLike, key: str):
        dest = self.s3_dir / key
        try:
            shutil.copy(file_path, dest)
        except Exception as e:
            print(e, file=sys.stderr)

    def register_run(self, run: Run):
        self.runs[run.id] = run

    def update_db(self, run: Run):
        pass

    def get_run(self, run_id: str) -> Run:
        return self.runs[run_id]

    def add_points_to_run(self, run: Run, points: List[Point]):
        self.runs[run.id].points = points
