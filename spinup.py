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
import prettytable
import os.path
import urllib2
import hashlib
import novaclient.exceptions
import pyrax.exceptions


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

    def run(self):
        print "Starting spinup : Username: %s , Region: %s" \
            % (self.username, self.region)

        self.run_tag = self.id_generator(4)
        self.desired_count = template_args['server']['desired_count']
        self.error_prediction_pct = \
            template_args['server']['error_prediction_pct']
        self.image_id = template_args['server']['image_id']
        self.flavor_id = template_args['server']['flavor_id']

        self.build_timeout = template_args['server']['build_timeout']
        self.total_timeout = template_args['server']['total_timeout']
        self.check_interval = template_args['server']['check_interval']

        self.delete_failed = template_args['server']['delete_failed']
        self.delete_success = template_args['server']['delete_success']

        self.rackconnect = template_args['server']['rackconnect']
        self.stats_file = template_args['server']['stats_file']
        self.sshkey_name = template_args['server']['sshkey_name']

        self.calc_count = self.desired_count + int(
            math.ceil((self.error_prediction_pct/100)*self.desired_count))

        self.image_name = self.get_image_name(self.image_id)
        logging.info("Building servers::"
                     " Image Name: %s "
                     " Image ID: %s,"
                     " Flavor ID: %s ,"
                     " Desired Count: %d,"
                     " Calculated Count: %d,"
                     " Build timeout: %s ,"
                     " Total Timeout: %d,"
                     " Delete if failed: %s,"
                     " Delete if success: %s,"
                     " Rackconnect: %s,"
                     " Statistics File: %s" %
                     (self.image_name,
                      self.image_id,
                      self.flavor_id,
                      self.desired_count,
                      self.calc_count,
                      self.build_timeout,
                      self.total_timeout,
                      self.delete_failed,
                      self.delete_success,
                      self.rackconnect,
                      self.stats_file))
        for ctr in xrange(0, self.calc_count):
            self.build_one()
        self.watch_build()

    def watch_build(self):
        ctr = 0
        success = 0
        failed = 0
        while ctr < self.total_timeout:
            for s in self.server_list:
                try:
                    srv = self.cs.servers.get(s['id'])
                    s['build_status'] = srv.status
                    s['build_time'] = s['build_time'] + self.check_interval
                    if s['status'] != 'SUCCESS':
                        if srv.status == "ACTIVE":
                            logging.info("Build complete for %s %s" %
                                         (srv.name, srv.id))
                            s['primary_ip'] = srv.accessIPv4
                            run_health_check = False
                            if 'rackconnect' in self.template_args['server']:
                                if self.template_args['server']['rackconnect']:
                                    if self.get_rackconnect_status(srv):
                                        run_health_check = True
                            if run_health_check:
                                if self.health_check(s['primary_ip']):
                                    success = success + 1
                                    s['status'] = 'SUCCESS'
                                else:
                                    s['status'] = 'FAILED'
                                    failed = failed + 1
                                    if self.delete_failed:
                                        srv.delete()
                                    self.build_one()
                        else:
                            if s['build_time'] >= self.build_timeout:
                                logging.info("Build timeout reached for %s %s"
                                             % (srv.name, srv.id))
                                logging.info("Deleting server %s" % (srv.id))
                                if self.delete_failed:
                                    srv.delete()
                                s['status'] = 'FAILED'
                                failed = failed + 1
                                self.build_one()
                    if success == self.desired_count:
                        logging.info("Desired count reached %d"
                                     % (self.desired_count))
                        print ("Desired count reached %d"
                               % (self.desired_count))
                        self.cleanup_build()
                        return
                except (novaclient.exceptions.NotFound, pyrax.exceptions.NotFound) as err:
                    logging.debug("Caught novaclient.exceptions.NotFound exception for %s"
                                  % (s['id']))
                    continue
                time.sleep(self.check_interval)
                ctr = ctr + self.check_interval
        if ctr >= self.total_timeout:
            logging.info("Total timeout reached %d seconds"
                         % (self.total_timeout))
            self.cleanup_build()

    def build_one(self):
        if self.image_name.find('Windows') == -1:
            is_linux = True
        else:
            is_linux = False
        s_name = self.run_tag + "-" + self.id_generator(8)
        logging.info("Building server %s" % (s_name))
        if is_linux:
            if self.sshkey_name:
                s_create = self.cs.servers.create(
                    s_name,
                    self.image_id,
                    self.flavor_id,
                    key_name=self.sshkey_name)
            else:
                s_create = self.cs.servers.create(
                    s_name,
                    self.image_id,
                    self.flavor_id)
        else:
            s_create = self.cs.servers.create(
                s_name,
                self.image_id,
                self.flavor_id)

        self.server_list.append({'id': s_create.id,
                                'name': s_name,
                                'image_name': self.image_name,
                                'image_id': self.image_id,
                                'flavor_id': self.flavor_id,
                                'root_pass': s_create.adminPass,
                                'build_time': 0,
                                'status': 'STARTED',
                                'build_status': 'UNKNOWN',
                                'primary_ip': '0.0.0.0'})

    def health_check(self, ip):
        retries = self.template_args['server']['tests']['retries']
        test_count = 0
        port_test = {}
        url_test = False
        while test_count < retries:
            if 'ports' in self.template_args['server']['tests']:
                if self.template_args['server']['tests']['ports'] is not None:
                    port_list = str(self.template_args['server']['tests']['ports']).split(",")
                    for p in port_list:
                        if p in port_test:
                            if port_test[p] != 'SUCCESS':
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                result = s.connect_ex((ip, int(p)))
                                if(result == 0):
                                    logging.info("Attempt %d Health check for IP %s ,"
                                                 " port %s succeeded" % (test_count, ip, p))
                                    port_test[p] = 'SUCCESS'
                                else:
                                    logging.info("Attempt %d Health check for IP %s ,"
                                                 " port %s failed" % (test_count, ip, p))
                                    port_test[p] = 'FAILED'
                                s.close()
                        else:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            result = s.connect_ex((ip, int(p)))
                            if(result == 0):
                                logging.info("Attempt %d Health check for IP %s ,"
                                             " port %s succeeded" % (test_count, ip, p))
                                port_test[p] = 'SUCCESS'
                            else:
                                logging.info("Attempt %d Health check for IP %s ,"
                                             " port %s failed" % (test_count, ip, p))
                                port_test[p] = 'FAILED'
                            s.close()
                    port_test_failed = False
                    for pk, pv in port_test.items():
                        if pv == 'FAILED':
                            port_test_failed = True
            if not port_test_failed:
                if 'url' in self.template_args['server']['tests']:
                    if self.template_args['server']['tests']['url'] is not None:
                        if not url_test:
                            try:
                                url = "http://" + ip + \
                                    self.template_args['server']['tests']['url']
                                urlobj = urllib2.urlopen(url, timeout=5)
                                urldata = urlobj.read()
                                sha1 = hashlib.sha1()
                                sha1.update(urldata)
                                if sha1.hexdigest() != \
                                        self.template_args['server']['tests']['url_sha1']:
                                    logging.info("Health check for URL %s ,"
                                                 " failed " % (url))
                                else:
                                    logging.info("Health check for URL %s ,"
                                                 " succeeded " % (url))
                                    url_test = True
                            except urllib2.URLError:
                                logging.info("Health check for URL %s ,"
                                             " failed " % (url))
            else:
                if 'url' in self.template_args['server']['tests']:
                    logging.info("Url checks skipped because port checks failed")
            if url_test and not port_test_failed:
                return(True)
            test_count = test_count + 1
            time.sleep(1)
        return(False)

    def cleanup_build(self):
        logging.info("Cleaning up build")
        for s in self.server_list:
            srv = self.cs.servers.get(s['id'])
            s['build_status'] = srv.status
            if s['status'] != 'SUCCESS' and self.delete_failed:
                logging.info("Deleting server %s in %s status" %
                             (srv.id, s['build_status']))
                srv.delete()
                s['status'] = 'DELETED'

            if s['status'] == 'SUCCESS' and self.delete_success:
                logging.info("Deleting server %s in %s status" %
                             (srv.id, s['build_status']))
                srv.delete()
                s['status'] = 'DELETED_SUCCESS'

    def print_summary(self):
        headers = [u'name', u'end-status', u'build-status',
                   u'build-time', u'flavor-id', u'primary-ip',
                   u'server-id']
        pt = prettytable.PrettyTable(headers)
        pt.align["name"] = 'l'
        pt.align["flavor_id"] = 'l'
        for s in self.server_list:
            tds = []
            tds.append(s['name'])
            tds.append(s['status'])
            tds.append(s['build_status'])
            tds.append(s['build_time'])
            tds.append(s['flavor_id'])
            tds.append(s['primary_ip'])
            tds.append(s['id'])
            pt.add_row(tds)
        print pt.get_string()

    def register_stats(self):
        if self.template_args['server']['stats_file']:
            if os.path.isfile(template_args['server']['stats_file']):
                stats = open(template_args['server']['stats_file'], 'a+')
            else:
                stats = open(template_args['server']['stats_file'], 'w')
                stats.write('image_name,image_id,flavor_id,'
                            "build_status,build_time\n")

            for s in self.server_list:
                stats.write("%s,%s,%s,%s,%s\n" % (
                            s['image_name'],
                            s['image_id'],
                            s['flavor_id'],
                            s['build_status'],
                            s['build_time']))

    def id_generator(self, size=6,
                     chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def get_image_name(self, image_id):
        imgs = self.cs.images.list()
        for img in imgs:
            if img.id == image_id:
                return img.name
        return 'NOTFOUND'

    def get_rackconnect_status(self, srv):
        for key, value in srv.metadata.items() :
            if key == 'rackconnect_automation_status':
                if value == 'DEPLOYED':
                    return True
        return False


def print_usage():
    print "usage: spinup "
    print "Arguments: "
    "--help     : This help"
    "--username : Rackspace Cloud username or environment variable OS_USERNAME"
    "--apikey   : Rackspace Cloud API key or environment variable OS_PASSWORD"
    "--region   : Rackspace Cloud region(ord,iad,lon,syd,hkg) or environment"
    " variable OS_PASSWORD"
    "--template : YAML template (use --templatehelp for more details)"
    "--templatehelp : Print detailed template help"


def template_help():
    print '''
log_file: Log file for operations
log_level: Log level

creds:
  username: Rackspace Cloud username. This also can be read from the
  environment variable OS_USERNAME or passed via the command line using
  --username.

  api_key: Rackspace Cloud api key. This also can be read from the
  environment variable OS_PASSWORD or passed via the command line using
  --apikey.

  region: Rackspace Cloud region(ord,iad,lon,syd,hkg). This also can be
  read from the environment variable OS_REGION or passed via the command
  line using --region.

server:
  image_id: Rackspace cloud server image ID.

  flavor_id: Rackspace cloud flavor ID.

  sshkey_name: SSH key if server type is Linux.

  tests: Define the tests that need to be performed for determining the
  sucess of the server build.

  ports: Comma separated list of ports. These ports will be scanned to make
  sure they are listening.

  url: A URL that can be used to check heath status. e.g. /health.php

  url_sha1:  A SHA checksum for the URL.

  retries: Number of times to try the tests.

  build_timeout: Number of seconds to wait before treating the server as
  failed. If the server is not active by then, it will be deleted.

  total_timeout: A grand total timeout after which the scripts aborts.

  check_interval: Intervals to check server status during the build process.
  If you set this too low, you may hit API limits.

  desired_count: Number of servers desired

  error_prediction_pct: An estimation of how many servers will fail the build.
  This is used to calculate the number of servers to start with. The values
  are rounded to the nearest integer.

  delete_failed: Delete servers that we consider failed. This includes the
  servers that took longer than build_timeout.

  delete_success: Delete servers in any case. Used for testing and playing.

  rackconnect: Are these servers rackconnected.

  stats_file: A file to which CSV results will be written.
    '''

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Spinup")
    parser.add_argument("--username", metavar="$OS_USERNAME",
                        help="Rackspace Cloud API key or environment "
                        "variable OS_USERNAME")
    parser.add_argument("--apikey", metavar="$OS_PASSWORD",
                        help="Rackspace Cloud API key or environment "
                        "variable OS_PASSWORD")
    parser.add_argument("--region", metavar="$OS_REGION_NAME",
                        help="Rackspace Cloud API key or environment "
                        "variable OS_REGION")
    parser.add_argument("--template", metavar="", help="YAML template "
                        "(use --templatehelp for more details)")
    parser.add_argument("--templatehelp", help="Print detailed "
                        "template help", action='store_true')

    args = parser.parse_args()

    if args.templatehelp:
        template_help()
        sys.exit(0)

    if args.template:
        stream = open(args.template, 'r')
        template_args = yaml.safe_load(stream)
    else:
        logging.debug("Yaml template not provided on the command line.")
        print_usage()

    if template_args['log_file']:
        log_file = template_args['log_file']
    else:
        log_file = "spinup.log"

    log_level = logging.INFO
    if template_args['log_level']:
        if template_args['log_level'] == 'debug':
            log_level = logging.DEBUG
        if template_args['log_level'] == 'info':
            log_level = logging.INFO

    logging.basicConfig(filename=log_file, level=log_level,
                        format='%(asctime)s [%(levelname)s] %(message)s')

    if args.username:
        username = args.username
    elif template_args['creds']['username']:
        username = template_args['creds']['username']
    elif os.environ.get("OS_USERNAME", None):
        logging.debug("Username not provided on command line")
        username = os.environ.get("OS_USERNAME")
    else:
        logging.debug("Username not found in yaml file.")
        print_usage()
        sys.exit(-1)

    if args.apikey:
        api_key = args.username
    elif template_args['creds']['api_key']:
        api_key = template_args['creds']['api_key']
    elif os.environ.get("OS_PASSWORD", None):
        logging.debug("API Key not provided on command line")
        api_key = os.environ.get("OS_PASSWORD")
    else:
        logging.debug("API Key not found in yaml file.")
        print_usage()
        sys.exit(-1)

    if args.region:
        region = args.region
    elif template_args['creds']['region']:
        region = template_args['creds']['region']
    elif os.environ.get("OS_REGION_NAME", None):
        logging.debug("Region not provided on command line")
        region = os.environ.get("OS_REGION_NAME")
    else:
        logging.debug("Region not found in yaml file.")
        print_usage()
        sys.exit(-1)

    logging.info("Connecting with username: %s ,"
                 "api key XXX, region %s" % (username, region))
    s = spinup(username, api_key, region, template_args)
    s.run()
    s.register_stats()
    s.print_summary()
