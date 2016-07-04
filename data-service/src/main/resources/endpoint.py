"""
   Copyright (c) 2016 Cisco and/or its affiliates.
   This software is licensed to you under the terms of the Apache License, Version 2.0
   (the "License").
   You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
   The code, technical concepts, and all information contained herein, are the property of
   Cisco Technology, Inc.and/or its affiliated entities, under various laws including copyright,
   international treaties, patent, and/or contract.
   Any use of the material herein must be in accordance with the terms of the License.
   All rights not expressly granted by the License are reserved.
   Unless required by applicable law or agreed to separately in writing, software distributed
   under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
   ANY KIND, either express or implied.
   Purpose: Discover API endpoints of a cluster.
"""

from cm_api.api_client import ApiResource

CLOUDERA = "Cloudera"


class Endpoint(object):
    """
    Object that abstracts an API service
    """
    def __init__(self, service_type, url):
        self.type = service_type
        self.url = url

    def gettype(self):
        """
        Get service type of endpoint
        :return: type of end point
        """
        return self.type

    def geturl(self):
        """
        URL to access endpoint API
        :return: URL String
        """
        return self.url


class Platform(object):
    """
    Platform module that discovers endpoint interfaces from management
    node.
    Currently it is tied to Cloudera and in future if we have Hortonworks then it needs
    to be extended to return HDFS and HBASE endpoints
    """
    def __init__(self):
        pass

    def discover(self, properties):
        """
        Disover API endpoints from cluster manager
        :param properties: properties containing defintion.
        :return:
        """
        pass

    @staticmethod
    def factory(distribution):
        """
        Factory method that returns Platform object based on hadoop distribution
        :param distribution - Provider name of hadoop distribution
        :return: Platform object
        """
        if distribution == ("%s" % CLOUDERA):
            return Cloudera()
        elif distribution == "Local":
            return Local()




def connect_cm(cm_host, cm_username, cm_password):
    """
    Connects to Cloudera Manager API Resource instance to retrieve Endpoint details
    :param cm_host: Cloudera Manager host
    :param cm_username: Username for authentication
    :param cm_password: Password for authentication
    :return:
    """
    api = ApiResource(cm_host, version=6, username=cm_username, password=cm_password)
    cm_manager = api.get_cloudera_manager()
    return api, cm_manager


class Cloudera(Platform):
    """
    Cloudera Endpoint object that discovers endpoint of an
    hadoop cluster depending on the distribution
    """

    def discover(self, properties):
        endpoints = {}
        api, _ = connect_cm(properties['cm_host'], properties['cm_user'], properties['cm_pass'])
        cluster_name = ""
        for cluster_detail in api.get_all_clusters():
            cluster_name = cluster_detail.name
            break
        print 'getting ' + cluster_name
        cluster = api.get_cluster(cluster_name)
        for service in cluster.get_all_services():
            if service.type == "HDFS":
                for role in service.get_all_roles():
                    if role.type == "HTTPFS":
                        webhdfs_host = '%s:14000' % api.get_host(role.hostRef.hostId).hostname
                        endpoints['HDFS'] = Endpoint("HDFS", webhdfs_host)
                        break
            elif service.type == "HBASE":
                for role in service.get_all_roles():
                    if role.type == "HBASETHRIFTSERVER":
                        hbase_host = '%s' % api.get_host(role.hostRef.hostId).hostname
                        endpoints['HBASE'] = Endpoint("HBASE", hbase_host)
                        break
        return endpoints


class Local(Platform):
    """
    Platform instance used  for testing purpose
    """
    def discover(self, properties):
        endpoints = {"HDFS": Endpoint("HDFS", "192.168.33.10:50070"),
                     'HBASE': Endpoint("HBASE", "192.168.33.10")}
        return endpoints
