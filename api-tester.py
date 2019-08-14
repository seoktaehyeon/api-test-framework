#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from utils.SwaggerParser import SwaggerParser
import os
import sys


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(u'%s option' % sys.argv[0])
        print(u'option: init | run')
        exit(1)
    if sys.argv[1] == 'init':
        sp = SwaggerParser()
        for _doc in sp.api_doc_list:
            sp.parse_doc(doc_file_name=_doc)
    elif sys.argv[1] == 'run':
        _html_report = os.path.join('output', 'report.html')
        pytest.main([
            '-v',
            '--color=yes',
            '--html=%s' % _html_report,
            '--capture=no'
        ])
