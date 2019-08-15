#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from utils.SwaggerParser import SwaggerParser
import os
import sys


def help_doc():
    _help_doc = '\n'.join([
        'Usage: %s option' % sys.argv[0],
        'option:',
        '    init    Init test case and generate data template in data_template dir',
        '    run     Run test case',
    ])
    print(_help_doc)
    exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        help_doc()
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
    else:
        help_doc()
