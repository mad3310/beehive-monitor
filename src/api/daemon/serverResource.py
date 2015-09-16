__author__ = 'mazheng'

from utils.invokeCommand import InvokeCommand
from daemonResource import ServerResource


class CPURatio(ServerResource):

    def __init__(self):
        self.file = "/proc/stat"
        self.total_cpu = 0
        self.total_cpu_inc = 0
        self.total_user_cpu = 0
        self.total_system_cpu = 0

        self.total_user_ratio = 0
        self.total_system_ratio = 0

        self.child_cpus = {}
        self.child_user_cpus = {}
        self.child_system_cpus = {}

        self.child_user_ratios = {}
        self.child_system_ratios = {}

    @property
    def cpu_inc(self):
        return self.total_cpu_inc

    @staticmethod
    def _cal_ratio(numerator, denominator):
        return 1.0 * numerator / denominator

    def statistic(self):
        ivk_cmd = InvokeCommand()
        cmd = 'grep -E cpu %s' % self.file
        content = ivk_cmd._runSysCmd(cmd)[0]
        cpu_list = content.strip().split('\n')
        total_cpu_list = map(int, cpu_list[0].split()[1:])
        self.count_total_cpu(total_cpu_list)

        childs_cpu_list = cpu_list[1:]
        self.count_child_cpu(childs_cpu_list)

    def count_total_cpu(self, total_cpu_list=[]):
        tmp_total_cpu = reduce(lambda x, y: x + y, total_cpu_list)
        tmp_total_user_cpu = total_cpu_list[0]
        tmp_total_system_cpu = total_cpu_list[2]
        if self.total_cpu and self.total_user_cpu and self.total_system_cpu:
            self.total_cpu_inc = tmp_total_cpu - self.total_cpu
            self.total_user_ratio = 1.0 * \
                (tmp_total_user_cpu - self.total_user_cpu) / (self.total_cpu_inc)
            self.total_system_ratio = 1.0 * \
                (tmp_total_system_cpu - self.total_system_cpu) / (self.total_cpu_inc)
        self.total_cpu = tmp_total_cpu
        self.total_user_cpu = tmp_total_user_cpu
        self.total_system_cpu = tmp_total_system_cpu

    def count_child_cpu(self, childs_cpu_list=[]):
        for i in range(len(childs_cpu_list)):
            child_cpu_list = map(int, childs_cpu_list[i].split()[1:])
            tmp_child_cpu = reduce(lambda x, y: x + y, child_cpu_list)
            tmp_child_user_cpu = child_cpu_list[0]
            tmp_child_system_cpu = child_cpu_list[2]
            if self.child_cpus.get(i, 0) and self.child_user_cpus.get(i, 0) and self.child_system_cpus.get(i, 0):
                cpu_inc = tmp_child_cpu - self.child_cpus[i]
                self.child_user_ratios[i] = self._cal_ratio(
                    (tmp_child_user_cpu - self.child_user_cpus[i]), cpu_inc)
                self.child_system_ratios[i] = self._cal_ratio(
                    (tmp_child_system_cpu - self.child_system_cpus[i]), cpu_inc)
            self.child_cpus[i] = tmp_child_cpu
            self.child_user_cpus[i] = tmp_child_user_cpu
            self.child_system_cpus[i] = tmp_child_system_cpu

    def get_result(self):
        self.statistic()
        result = {}
        result['total'] = self._make_result(
            self.total_user_ratio, self.total_system_ratio)
        for i in self.child_user_ratios.keys():
            result['cpu' + str(i)] = self._make_result(
                self.child_user_ratios[i], self.child_system_ratios[i])
        return result

    def _make_result(self, user, system):
        return {"user": user, "system": system}
