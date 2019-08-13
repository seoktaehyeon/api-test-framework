#!/usr/local/env python3
# -*- coding: utf-8 -*-

import pytest
from utils.SwaggerParser import SwaggerParser
import os
import sys


if __name__ == '__main__':
    if sys.argv[1] == 'prepare':
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
