#!/usr/bin/env python
# encoding: utf-8

import logging
from elasticsearch import Elasticsearch

logging.basicConfig()

ES_TEST_CLUSTER_HOSTS = [
    {"host": "10.140.65.12", "port": 9200},
    {"host": "10.140.65.13", "port": 9200},
    {"host": "10.140.65.14", "port": 9200}
]

es_test_cluster = Elasticsearch(
    ES_TEST_CLUSTER_HOSTS,
    sniff_on_start=False,
    sniff_on_connection_fail=True,
    sniffer_timeout=300,
    sniff_timeout=5,
)
