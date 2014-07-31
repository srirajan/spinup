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

logging.basicConfig(filename="spinup.log", level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] %(message)s')


class spinup:

    def __init__(self, username=None, api_key=None,
                 region=None, template_args=None):
        self.username = username
        self.api_key = api_key
        self.region = region
        self.template_args = template_args
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_setting("region", region)
        try:
            pyrax.set_credentials(username, api_key, region=region)
        except pyrax.exc.AuthenticationFailed:
            logging.debug("Pyrax login failed for %s", (username))
        self.cs = pyrax.cloudservers
        if self.cs is None:
            logging.debug("Failed to get cloud server object")

    def id_generator(self, size=6,
                     chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    def run(self):
        print "Starting"
        print "Username: %s , Region: %s" % (self.username, self.region)

        run_tag = self.id_generator(4)
        count = template_args['server']['count']
        image = template_args['server']['image']
        flavor = template_args['server']['flavor']
        build_timeout = template_args['server']['build_timeout']
        total_timeout = template_args['server']['total_timeout']
        delete_failed = template_args['server']['delete_failed']
        delete_success = template_args['server']['delete_success']
        rackconnect = template_args['server']['rackconnect']
        stats_file = template_args['server']['stats_file']
        logging.info("Building servers with Image: %s, Flavor: %s ,"
                     " Count: %d, Build timeout: %s Total Timeout: %d,"
                     " Delete if failed: %s, Delete if success: %s,"
                     " Rackconnect: %s, Statistics File: %s" %
                     (image, flavor, count, build_timeout, total_timeout,
                      delete_failed, delete_success, rackconnect, stats_file))

        for ctr in xrange(0, count):
            s_name = run_tag + "-" + self.id_generator(8)

            logging.info("Building server %s" % (s_name))


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
