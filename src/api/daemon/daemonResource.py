__author__ = 'mazheng'


class DaemonResource(object):

    def statistic(self, *args):
        raise NotImplemented("statistic method should be implemented!")

    def get_result(self):
        raise NotImplemented("get result method should be implemented!")


class ContainerResource(DaemonResource):

    def __init__(self, container_id):
        self._container_id = container_id

    @property
    def container_id(self):
        return self._container_id


class ServerResource(DaemonResource):

    '''TODO'''
