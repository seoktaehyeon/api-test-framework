#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


def get_global():
    return {
        'access_url': os.getenv('TEST_SERVER_URL'),
        'account': os.getenv('TEST_ACCOUNT'),
        'password': os.getenv('TEST_PASSWORD'),
    }

