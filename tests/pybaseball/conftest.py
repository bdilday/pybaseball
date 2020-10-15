import os
import urllib.parse
from typing import Callable, Dict, Union
from unittest.mock import MagicMock

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_delete(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.delete', after=thrower))
    monkeypatch.setattr(requests, 'delete', mock)
    return mock


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_get(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.get', after=thrower))
    monkeypatch.setattr(requests, 'get', mock)
    return mock


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_head(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.head', after=thrower))
    monkeypatch.setattr(requests, 'head', mock)
    return mock


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_options(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.options', after=thrower))
    monkeypatch.setattr(requests, 'options', mock)
    return mock


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_patch(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.patch', after=thrower))
    monkeypatch.setattr(requests, 'patch', mock)
    return mock


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_put(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.put', after=thrower))
    monkeypatch.setattr(requests, 'put', mock)
    return mock


# Autouse to prevent integration tests sneaking into the unit tests
@pytest.fixture(autouse=True)
def _requests_prevent_post(monkeypatch: MonkeyPatch, thrower: Callable, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect(f'requests.post', after=thrower))
    monkeypatch.setattr(requests, 'post', mock)
    return mock


# Autouse to prevent file system side effects
@pytest.fixture(autouse=True, name="mkdir")
def _mkdir(monkeypatch: MonkeyPatch, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect('pathlib.Path.mkdir'))
    monkeypatch.setattr('pathlib.Path.mkdir', mock)
    return mock


# Autouse to prevent file system side effects
@pytest.fixture(autouse=True, name="remove")
def _remove(monkeypatch: MonkeyPatch, logging_side_effect: Callable) -> MagicMock:
    mock = MagicMock(side_effect=logging_side_effect('os.remove'))
    monkeypatch.setattr(os, 'remove', mock)
    return mock


@pytest.fixture()
def response_get_monkeypatch(monkeypatch: MonkeyPatch) -> Callable:
    """
        Returns a function that will monkeypatch the requests.get function call to return expected data 
    """
    def setup(result: Union[str, bytes], expected_url: str = None) -> None:
        """
           Get the DatFrame representation of the contents of a csv file in the tests data directory


            ARGUMENTS:
            result          : str            : the payload to return in the contents of the request.get call
            expected_url    : str (optional) : an expected_url to test the get call against
                                               to ensure the correct endpoint is hit
        """
        def _monkeypatch(url: str, params: Dict = None, timeout: int = None) -> object:
            final_url = url

            if params:
                query_params = urllib.parse.urlencode(params, safe=',')
                final_url = f"{final_url}?{query_params}"

            if expected_url is not None:
                # These prints are desired as these are long and get cut off in the test outpute.
                # These will only render on failed tests, so only when you would want to see them anyway.
                print("expected", expected_url)
                print("received", final_url)
                assert final_url.endswith(expected_url)

            class DummyResponse:
                def __init__(self, content: Union[str, bytes]):
                    self.content = content
                    self.status_code = 200

            return DummyResponse(result)

        monkeypatch.setattr(requests, 'get', _monkeypatch)

    return setup
