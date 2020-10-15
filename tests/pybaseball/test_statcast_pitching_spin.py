from typing import Callable

import pandas as pd
import pytest

import pybaseball.statcast_pitcher_spin as spin

from ..conftest import SIG_DIG, GetDataFrameCallable

rounding_error_columns = ['vxR', 'vyR', 'vxbar', 'vybar', 'vbar']


@pytest.fixture(name="test_frame")
def _test_frame(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('statcast_spin_test_data.csv').round(SIG_DIG)


@pytest.fixture(name="target_frame")
def _target_frame(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('statcast_spin_target_data.csv').round(SIG_DIG)


def test_individual_calculations(compare_almost_equal_dataframe: Callable, test_frame: pd.DataFrame,
                                 target_frame: pd.DataFrame) -> None:
    """
    Testing Mechanism that compares test data to target data for each
    calculation in the test_dict.

    This structure was preferable to creating individual funciton test
    because some values depend on the results of prior calculations
    """

    test_dict = {
        'find_release_point': ['yR'],
        'find_release_time': ['tR'],
        'find_release_velocity_components': ['vxR', 'vyR', 'vzR'],
        'find_flight_time': ['tf'],
        'find_average_velocity_components': ['vxbar', 'vybar', 'vzbar'],
        'find_average_velocity': ['vbar'],
        'find_average_drag': ['adrag'],
        'find_magnus_acceleration_magnitude': ['amagx', 'amagy', 'amagz'],
        'find_average_magnus_acceleration': ['amag'],
        'find_magnus_magnitude': ['Mx', 'Mz'],
        'find_phi': ['phi'],
        'find_lift_coefficient': ['Cl'],
        'find_spin_factor': ['S'],
        'find_transverse_spin': ['spinT'],
        'find_spin_efficiency': ['spin eff'],
        'find_theta': ['theta'],
    }

    for method, columns in test_dict.items():
        func = getattr(spin, method)
        test_frame = func(test_frame)

        compare_almost_equal_dataframe(test_frame[columns], target_frame[columns], rounding_error_columns)
