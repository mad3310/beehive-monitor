#!/usr/bin/env python
# encoding: utf-8

import pytest

from container_monitor.utils import diskio


@pytest.mark.parametrize("value, expected", [
    (10000, '9.8 K/s'),
    (100001221, '95.4 M/s')
])
def test_bytes2human(value, expected):
    assert diskio.bytes2human(value), expected
