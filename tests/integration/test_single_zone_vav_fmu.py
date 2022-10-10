import os
from datetime import datetime
from time import sleep
from unittest import TestCase

import pytest
from alfalfa_client.alfalfa_client import AlfalfaClient


@pytest.mark.integration
class TestSingleZoneVAVFMU(TestCase):

    def test_simple_internal_clock(self):
        alfalfa = AlfalfaClient(url='http://localhost')
        fmu_path = os.path.join(os.path.dirname(__file__), 'models', 'single_zone_vav.fmu')
        model_id = alfalfa.submit(fmu_path)

        alfalfa.wait(model_id, "READY")

        end_datetime = datetime(2019, 1, 1, 0, 5)
        alfalfa.start(
            model_id,
            external_clock="false",
            start_datetime=datetime(2019, 1, 1),
            end_datetime=end_datetime,
            timescale=5
        )

        alfalfa.wait(model_id, "RUNNING")
        # wait for model to advance for 1 minute at timescale 5
        sleep(60)
        alfalfa.wait(model_id, "COMPLETE")
        model_time = alfalfa.get_sim_time(model_id)
        assert end_datetime.strftime("%Y-%m-%d %H:%M") in model_time
