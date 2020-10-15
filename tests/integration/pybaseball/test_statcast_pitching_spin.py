from typing import Callable

import pandas as pd
import pytest

import pybaseball.statcast_pitcher_spin as spin

from ...conftest import SIG_DIG, GetDataFrameCallable

rounding_error_columns = ['Mz']


@pytest.fixture(name="template_data")
def _template_data(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('statcast_sping_live_Darvish_July2019_test.csv').round(SIG_DIG)


def test_statcast_pitcher_spin(compare_almost_equal_dataframe: Callable, template_data: pd.DataFrame) -> None:
    """
    Testing the full data stream from web-scraping to calculated answers

    Answers were calculated using Prof. Alan Nathan's MovementSpinEfficiencyTemplate.xlsx
    featured on http://baseball.physics.illinois.edu/pitchtracker.html

    This example is of Yu Darvish(506433) from 2019-07-01 to 2019-07-31
    Darvish has a wide variety of pitches, giving the most diverse set of test data

    """

    # Run the method in question
    df = spin.statcast_pitcher_spin(start_dt='2019-07-01', end_dt='2019-07-31', player_id=506433)

    # Columns needed to be checked
    target_columns = ['Mx', 'Mz', 'phi', 'theta']

    compare_almost_equal_dataframe(df[target_columns], template_data[target_columns], rounding_error_columns)
