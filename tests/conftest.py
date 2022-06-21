# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for alfalfa.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""


from pathlib import Path

import pytest

from alfalfa_worker.dispatcher import Dispatcher
from tests.worker.lib.mock_dispatcher import MockDispatcher
from tests.worker.lib.mock_run_manager import MockRunManager


@pytest.fixture
def dispatcher(tmp_path: Path):
    """Regular dispatcher with MockRunManager.
    Use for running MockJobs locally"""
    run_dir = tmp_path / 'runs'
    s3_dir = tmp_path / 's3'
    dispatcher = Dispatcher(run_dir)
    dispatcher.run_manager = MockRunManager(run_dir, s3_dir)
    yield dispatcher


@pytest.fixture
def mock_dispatcher(tmp_path: Path):
    """MockDispatcher with regular RunManager.
    Use for running regular jobs in Docker"""
    dispatcher = MockDispatcher(tmp_path)
    yield dispatcher
