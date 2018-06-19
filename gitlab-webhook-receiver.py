#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" Gitlab Webhook Receiver """
# Based on: https://github.com/schickling/docker-hook

import json
import yaml
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
try:
    # For Python 3.0 and later
    from http.server import HTTPServer
    from http.server import BaseHTTPRequestHandler
except ImportError:
    # Fall back to Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer as HTTPServer
import sys
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG,
                    stream=sys.stdout)


class RequestHandler(BaseHTTPRequestHandler):
    """A POST request handler."""

    # Attributes (only if a config YAML is used)
    # command, gitlab_token, foreground
    def get_info_from_config(self, project, config):
        # get command and token from config file
        self.command = config[project]['command']
        self.gitlab_token = config[project]['gitlab_token']
        self.foreground = 'background' in config[project] and not config[project]['background']
        logging.info("Load project '%s' and run command '%s'", project, self.command)

    def do_token_mgmt(self, gitlab_token_header, json_payload):
        # Check if the gitlab token is valid
        if gitlab_token_header == self.gitlab_token:
            logging.info("Start executing '%s'" % self.command)
            try:
                # run command in background
                p = Popen(self.command, stdin=PIPE)
                p.stdin.write(json_payload);
                if self.foreground:
                    p.communicate()
                self.send_response(200, "OK")
            except OSError as err:
                self.send_response(500, "OSError")
                logging.error("Command could not run successfully.")
                logging.error(err)
        else:
            logging.error("Not authorized, Gitlab_Token not authorized")
            self.send_response(401, "Gitlab Token not authorized")

    def do_POST(self):
        logging.info("Hook received")

        if sys.version_info >= (3,0):
            # get payload
            header_length = int(self.headers['Content-Length'])
            # get gitlab secret token
            gitlab_token_header = self.headers['X-Gitlab-Token']
        else:
            header_length = int(self.headers.getheader('content-length', "0"))
            gitlab_token_header = self.headers.getheader('X-Gitlab-Token')

        json_payload = self.rfile.read(header_length)
        json_params = {}
        if len(json_payload) > 0:
            json_params = json.loads(json_payload.decode('utf-8'))

        try:
            # get project homepage
            project = json_params['project']['name']
        except KeyError as err:
            self.send_response(500, "KeyError")
            logging.error("No project provided by the JSON payload")
            self.end_headers()
            return

        try:
            self.get_info_from_config(project, config)
            self.do_token_mgmt(gitlab_token_header, json_payload)
        except KeyError as err:
            self.send_response(500, "KeyError")
            if err == project:
                logging.error("Project '%s' not found in %s", project, args.cfg.name)
            elif err == 'command':
                logging.error("Key 'command' not found in %s", args.cfg.name)
            elif err == 'gitlab_token':
                logging.error("Key 'gitlab_token' not found in %s", args.cfg.name)
        finally:
            self.end_headers()


def get_parser():
    """Get a command line parser."""
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--addr",
                        dest="addr",
                        default="0.0.0.0",
                        help="address where it listens")
    parser.add_argument("--port",
                        dest="port",
                        type=int,
                        default=8666,
                        metavar="PORT",
                        help="port where it listens")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cfg",
                       dest="cfg",
                       default="config.yaml",
                       type=FileType('r'),
                       help="path to the config file")
    return parser


def main(addr, port):
    """Start a HTTPServer which waits for requests."""
    httpd = HTTPServer((addr, port), RequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if args.cfg:
        config = yaml.load(args.cfg)

    main(args.addr, args.port)
