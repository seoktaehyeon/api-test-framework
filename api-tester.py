#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from utils.SwaggerParser import SwaggerParser
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)


def help_doc():
    _help_doc = '\n'.join([
        'Usage: %s option' % sys.argv[0],
        'option:',
        '    init    Init test case and generate data template in data_template dir',
        '    run     Run test case',
        '    clean   Clean up workspace'
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
    elif sys.argv[1] == 'clean':
        rm_dir_list = [
            os.path.join('tests', 'test_case'),
            os.path.join('tests', 'test_data'),
            os.path.join('tests', 'data_template')
        ]
        for _dir in rm_dir_list:
            logging.info('Cleanup ext dir: %s' % _dir)
            subprocess.getoutput('rm -rf %s' % _dir)
            os.mkdir(_dir)
        logging.info('Cleanup ext dir: tests/test_env')
        subprocess.getoutput('cd tests && rm -rf test_env && cp -R test_env_template test_env')
    else:
        help_doc()
