#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import division
import yaml
import argparse
import logging
import os
import sys
import pprint
import pyrax
import string
import random
import random
import math
import time
import socket

logging.basicConfig(filename="spinup.log", level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s')


class spinup:

    server_list = []

    def __init__(self, username=None, api_key=None,
                 region=None, template_args=None):
        self.username = username
        self.api_key = api_key
        self.region = region.upper()
        self.template_args = template_args
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_setting("region", region)
        try:
            pyrax.set_credentials(self.username, self.api_key,
                                  region=self.region)
        except pyrax.exc.AuthenticationFailed:
            logging.debug("Pyrax login failed for %s", (username))
        self.cs = pyrax.cloudservers
        if self.cs is None:
            logging.debug("Failed to get cloud server object")
            print "Failed to get cloud server object."
            sys.exit(-1)

    def id_generator(self, size=6,
                     chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def get_server_os(self):
        print "__NOT_IMPLEMENTED__"

    def get_rackconnect_ip(self):
        print "__NOT_IMPLEMENTED__"

    def health_check(self, ip):
        if self.template_args['server']['tests']['ports'] is not None:
            port_list = str(self.template_args['server']['tests']['ports']).split(",")
            for p in port_list:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                p = int(p)
                result = s.connect_ex((ip, p))
                if(result == 0):
                    logging.info("Health check for IP %s ,"
                                 " port %s succeeded" % (ip, p))
                else:
                    logging.info("Health check for IP %s ,"
                                 " port %s failed" % (ip, p))
                s.close()
        sys.exit(0)

    def cleanup_build(self):
        for s in self.server_list:
            print s['name']

        for s in self.server_list:
            if s['status'] != 'SUCCESS':
                srv = self.cs.servers.get(s['id'])
                srv.delete()
                s['status'] = 'DELETED'

        for s in self.server_list:
            print s['name']

    def watch_build(self):
        ctr = 0
        success = 0
        while ctr < self.total_timeout:
            for s in self.server_list:
                srv = self.cs.servers.get(s['id'])
                s['build_time'] = s['build_time'] + self.check_interval
                if s['build_time'] >= self.build_timeout
                   and srv.status != "ACTIVE":

                    logging.info("Build timeout reached for %s %s" % (srv.name, srv.id))
                    logging.info("Deleting server %s" % (srv.id))
                    srv.delete()
                    s['status'] = 'FAILED'

                else:
                    if srv.status == "ACTIVE":
                        logging.info("Build complete for %s %s" % (srv.name, srv.id))
                        if self.health_check(srv.accessIPv4):
                            success = success + 1
                        s['status'] = 'SUCCESS'
                    if success == self.desired_count:
                        logging.info("Desired count reached")
                        print "Desired count reached"
                        self.cleanup_build()
                        sys.exit(0)
            time.sleep(self.check_interval)
            ctr = ctr + self.check_interval

    def run(self):
        print "Starting"
        print "Username: %s , Region: %s" % (self.username, self.region)

        self.run_tag = self.id_generator(4)
        self.desired_count = template_args['server']['desired_count']
        self.error_prediction_pct = template_args['server']['error_prediction_pct']
        self.image = template_args['server']['image']
        self.flavor = template_args['server']['flavor']

        self.build_timeout = template_args['server']['build_timeout']
        self.total_timeout = template_args['server']['total_timeout']
        self.check_interval = template_args['server']['check_interval']

        self.delete_failed = template_args['server']['delete_failed']
        self.delete_success = template_args['server']['delete_success']

        self.rackconnect = template_args['server']['rackconnect']
        self.stats_file = template_args['server']['stats_file']
        self.sshkey_name = template_args['server']['sshkey_name']

        self.calc_count = self.desired_count + int(math.ceil((self.error_prediction_pct/100)*self.desired_count))

        logging.info("Building servers with Image: %s, Flavor: %s ,"
                     " Desired Count: %d, Calculated Count: %d,"
                     " Build timeout: %s Total Timeout: %d,"
                     " Delete if failed: %s, Delete if success: %s,"
                     " Rackconnect: %s, Statistics File: %s" %
                     (self.image, self.flavor, self.desired_count, self.calc_count, self.build_timeout,
                      self.total_timeout, self.delete_failed, self.delete_success,
                      self.rackconnect, self.stats_file))

        for ctr in xrange(0, self.calc_count):
            s_name = self.run_tag + "-" + self.id_generator(8)
            logging.info("Building server %s" % (s_name))
            s_create = self.cs.servers.create(s_name,
                                self.image,
                                self.flavor)
            self.server_list.append({'id': s_create.id, 'name': s_name,
                                    'image': self.image, 'flavor': self.flavor,
                                    'root_pass': s_create.adminPass, 'build_time': 0,
                                    'status': 'STARTED'})
        self.watch_build()


def print_usage():
    print "usage: spinup --template [template file]"
    sys.exit(0)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Spinup")
    parser.add_argument("--username", metavar="OS_USERNAME",
                        help="Username for the Rackspace cloud")
    parser.add_argument("--apikey", metavar="OS_PASSWORD",
                        help="API Key for the Rackspace Cloud")
    parser.add_argument("--region", metavar="OS_REGION_NAME",
                        help="Region for the Rackspace Cloud")
    parser.add_argument("--template", metavar="", help="Yaml file")
    args = parser.parse_args()
    if args.template:
        stream = open(args.template, 'r')
        template_args = yaml.load(stream)
    else:
        logging.debug("Yaml template not provided on the command line.")
        print_usage()

    if args.username:
        username = args.username
    elif template_args['creds']['username']:
        username = template_args['creds']['username']
    elif os.environ.get("OS_USERNAME", None):
        logging.debug("Username not provided on command line")
        username = os.environ.get("OS_USERNAME")
    else:
        logging.debug("Username not found in yaml file.")

    if args.apikey:
        api_key = args.username
    elif template_args['creds']['api_key']:
        api_key = template_args['creds']['api_key']
    elif os.environ.get("OS_PASSWORD", None):
        logging.debug("API Key not provided on command line")
        api_key = os.environ.get("OS_PASSWORD")
    else:
        logging.debug("API Key not found in yaml file.")

    if args.region:
        region = args.region
    elif template_args['creds']['region']:
        region = template_args['creds']['region']
    elif os.environ.get("OS_REGION_NAME", None):
        logging.debug("Region not provided on command line")
        region = os.environ.get("OS_REGION_NAME")
    else:
        logging.debug("Region not found in yaml file.")

    logging.info("Connecting with username: %s ,"
                 "api key XXX, region %s" % (username, region))
    s = spinup(username, api_key, region, template_args)
    s.run()
