__author__ = 'mazheng'


import sched
import time
import threading


class AbstractScheduler(object):

    def __init__(self):
        self.sched = sched.scheduler(time.time, time.sleep)

    def _spawn(self, func, *args):
        thread = threading.Thread(target=func, args=args)
        thread.setDaemon(True)
        thread.start()

    def run_fixed_time(self, func, delay, *args):
        assert callable(func)

        def schedule():
            self.sched.enter(delay, 0, func, *args)
            self.sched.run()

        self._spawn(schedule)

    def run_cycle_time(self, func, period, *args):
        assert callable(func)

        def cycle(func, period, args):
            func(*args)
            self.sched.enter(period, 0, cycle, (func, period, args))

        def schedule():
            self.sched.enter(period, 0, cycle, (func, period, args))
            self.sched.run()

        self._spawn(schedule)

    def close(self):
        self.sched = None
