#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Sample module to bind to GitLab webhook request
# Usage: gitlab-webhook-receiver.py --module glhook
def main(token, payload, request, cmdargs):
    if token == "xxx":
        request.send_response(401, "Gitlab Token not authorized")
    else:
        print("foo")
        request.send_response(200, "OK")
