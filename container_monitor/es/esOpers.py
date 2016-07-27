#coding=utf-8
from elasticsearch import Elasticsearch
import logging
import datetime
from utils.es_utils import es_test_cluster

class esOpers(object):

    def __init__(self):
        self.es = es_test_cluster

    def get_all_source(self, index, ip, time_from, 
                        time_to, doc_type, size):
        res = self._get_all_values(index, ip, time_from, 
                             time_to, doc_type, size)
        ret = []
        for _res in res:
            if _res.has_key('_source'):
                ret.append(_res['_source'])
        return ret

    def _query_body(self, ip, time_from, time_to, doc_type):
        range_field = '%s.timestamp' % doc_type
        ip_field = '%s.ip' % doc_type
        body = {
                   'query': 
                   {
                      'bool': 
                      {
                         'must': [
                           {
                             'range': 
                             {
                                 range_field: 
                                 {
                                     'from':time_from,
                                     'to':  time_to 
                                 }
                             },
                           },
                           {
                             'term':
                             {
                                 ip_field : ip 
                             }
                           }
                        ]
                      }
                   }
                }
        return body

    def _get_all_values(self, index, ip, time_from, time_to, doc_type, size): 
        ret = []
        try:
            res = self.es.search(index = index, doc_type = doc_type, 
                  size = size, 
                  body = self._query_body(ip, time_from, time_to, doc_type))
            ret = res['hits']['hits']
        except Exception as e:
            logging.error("query in es fail")
            logging.error(e, exc_info=True)
        return ret

