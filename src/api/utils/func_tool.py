#!/usr/bin/env python
# encoding: utf-8

import time
import heapq
import functools


def lru_cache(maxsize):
    def decorate_func(f):
        cache = {}
        heap = []
        cursize = 0

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            key = repr(args)
            _cache=cache
            _heap=heap
            _heappop = heapq.heappop
            _heappush = heapq.heappush
            _time = time.time
            _cursize = cursize
            _maxsize = maxsize
            if key not in _cache:
                if _cursize == _maxsize:
                    (_, oldkey) = _heappop(_heap)
                    _cache.pop(oldkey)
                else:
                    _cursize += 1
                _cache[key] = f(*args, **kwargs)
                _heappush(_heap, (_time(), key))
                wrapper.misses += 1
            else:
                wrapper.hits += 1
            return cache[key]
        wrapper.hits = wrapper.misses = 0
        return wrapper
    return decorate_func


if __name__ == '__main__':

    @lru_cache(3)
    def test_func():
        return 1 << 10

    print test_func()
    print test_func()
    print test_func()
    print test_func()
    print test_func()
