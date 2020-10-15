import copy
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import MagicMock

import pandas as pd
import pytest
from typing_extensions import Protocol

from pybaseball import cache

SIG_DIG = 4  # Required because of read_csv bug in pandas

_ParseDates = Union[bool, List[int], List[str], List[List], Dict]




class GetDataFrameCallable(Protocol):  # pylint: disable=too-few-public-methods
    """
    This Protocol class is to be sure that we are passing the correct kind of Callable around in our tests.
    These are validated by MyPy at test time. Not at runtime (Python does not do runtime type checking).
    Protocols are a way to define that when we pass a function around
    (like we do in these tests to pass the functions in to load data),
    that the function sent over will take the correct typed parameters,
    and return the correct types.
    So in this instance we're defining that the type GetDataFrameCallable is a function that will
    take the params defined in __call__ and the return type defined in __call__.
    Further reading: https://docs.python.org/3/library/typing.html#typing.Protocol
    """
    def __call__(self, filename: str, parse_dates: _ParseDates = False) -> pd.DataFrame: ...


@pytest.fixture(name="data_dir")
def _data_dir() -> str:
    """
        Returns the path to the tests data directory
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, 'data')


@pytest.fixture()
def get_data_file_contents(data_dir: str) -> Callable[[str], str]:
    """
        Returns a function that will allow getting the contents of a file in the tests data directory easily
    """
    def get_contents(filename: str) -> str:
        """
            Get the str contents of a file in the tests data directory


            ARGUMENTS:
            filename    : str : the name of the file within the tests data directory to get the contents of
        """
        with open(os.path.join(data_dir, filename)) as _file:
            return _file.read()

    return get_contents


@pytest.fixture()
def get_data_file_dataframe(data_dir: str) -> GetDataFrameCallable:
    """
        Returns a function that will allow getting a dataframe from a csv file in the tests data directory easily
    """
    def get_dataframe(filename: str, parse_dates: _ParseDates = False) -> pd.DataFrame:
        """
            Get the DatFrame representation of the contents of a csv file in the tests data directory


            ARGUMENTS:
            filename    : str : the name of the file within the tests data directory to load into a DataFrame
        """
        return pd.read_csv(
            os.path.join(data_dir, filename),
            index_col=0,
            parse_dates=parse_dates
        ).reset_index(drop=True)

    return get_dataframe


@pytest.fixture(name='logging_side_effect')
def _logging_side_effect() -> Callable:
    def _logger(name: str, after: Optional[Callable] = None) -> Callable:
        def _side_effect(*args: Any, **kwargs: Any) -> Optional[Any]:
            logging.debug(f'Mock {name} => {args} {kwargs}')
            if after is not None:
                return after(*args, **kwargs)

            return None

        return _side_effect

    return _logger


@pytest.fixture(name='cache_config')
def _cache_config() -> cache.CacheConfig:
    test_cache_directory = os.path.join(cache.CacheConfig.DEFAULT_CACHE_DIR, '.pytest')
    config = cache.CacheConfig(enabled=False)
    config.cache_directory = test_cache_directory
    return config


@pytest.fixture(autouse=True)
def _override_cache_config(cache_config: cache.CacheConfig) -> None:
    def _test_auto_load() -> cache.CacheConfig:
        logging.debug('_test_auto_load')
        return cache_config

    # Copy this for when we want to test the autoload_cache function
    if not hasattr(cache.cache_config, '_autoload_cache'):
        # pylint: disable=protected-access
        cache.cache_config._autoload_cache = copy.copy(cache.cache_config.autoload_cache)  # type: ignore
    cache.cache_config.autoload_cache = _test_auto_load

    # Copy this for when we want to test the save function
    if not hasattr(cache.cache_config.CacheConfig, '_save'):
        # pylint: disable=protected-access
        cache.cache_config.CacheConfig._save = copy.copy(cache.cache_config.CacheConfig.save)  # type: ignore

    cache.cache_config.CacheConfig.save = MagicMock()  # type: ignore
    cache.config = cache_config
    cache.cache_record.cfg = cache_config


@pytest.fixture(name="assert_frame_not_equal")
def _assert_frame_not_equal() -> Callable:
    def _assert(*args: Any, **kwargs: Any) -> bool:
        try:
            pd.testing.assert_frame_equal(*args, **kwargs)
        except AssertionError:
            # frames are not equal
            return True
        else:
            # frames are equal
            raise AssertionError

    return _assert


@pytest.fixture(name="thrower")
def _thrower() -> Callable:
    def _raise(*args: Any, **kwargs: Any) -> None:
        raise Exception

    return _raise


@pytest.fixture(name='compare_almost_equal_series')
def _compare_almost_equal_series() -> Callable:
    def compare_almost_equal_series(s1: pd.Series, s2: pd.Series) -> None:
        """
        Almost equal was necessary due to rounding errors that would result
        from one value being calculated as .499999 and the next as .500000

        Printing `comp_df.query('diff > 0.0000`) will show that only 1 or 2
        values per calcuation rely on this function; the others are exactly
        equal
        """

        comp_df = pd.DataFrame()
        comp_df['left'] = s1.round(SIG_DIG)
        comp_df['right'] = s2.round(SIG_DIG)
        comp_df['diff'] = comp_df['left'] - comp_df['right']
        comp_df['diff'] = comp_df['diff'].abs().round(SIG_DIG)
        # print(comp_df.query('diff > 0.0000'))
        assert comp_df.query('diff > .0001').empty

    return compare_almost_equal_series


@pytest.fixture(name="compare_almost_equal_dataframe")
def _compare_almost_equal_dataframe(compare_almost_equal_series: Callable) -> Callable:
    def _compare_almost_equal_dataframe(df1: pd.DataFrame, df2: pd.DataFrame,
                                        rounding_error_columns: List[str]) -> None:
        for column in df1.columns:
            if column in rounding_error_columns:
                # Almost equal assertion is necessary for small differences that arise after consecutive calculations
                compare_almost_equal_series(df1[column], df2[column])
            else:
                pd.testing.assert_series_equal(df1[column], df2[column])

    return _compare_almost_equal_dataframe
