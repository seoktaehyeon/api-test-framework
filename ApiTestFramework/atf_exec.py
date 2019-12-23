#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from ApiTestFramework.SwaggerParser import SwaggerParser, CodeGenerator
import os
import sys
import subprocess
import logging
import yaml

logging.basicConfig(level=logging.INFO)


def help_doc():
    _help_doc = '\n'.join([
        'Usage: atf-exec option',
        'option:',
        '    init    Init framework',
        '    prepare Generate test case in test_case dir and data template in data_template dir',
        '    run     Run test case',
        '    clean   Clean up workspace'
    ])
    print(_help_doc)
    exit(1)


def init_atf_config():
    logging.info('Try to init ATF config')
    atf_config = dict()

    # Define root dir
    atf_root_path = os.path.abspath('.')
    atf_config['ATF_ROOT_PATH'] = atf_root_path

    # Define atf_config_path
    atf_config_path = os.path.join(atf_root_path, 'atf_config')
    atf_config['ATF_CONFIG_PATH'] = atf_config_path

    # Define API doc dir
    atf_api_doc_path = os.getenv('ATF_API_DOC_PATH')
    if atf_api_doc_path is None:
        atf_api_doc_path = os.path.join(atf_root_path, 'atf_api_docs')
    atf_config['ATF_API_DOC_PATH'] = atf_api_doc_path

    # Define test data template dir
    atf_test_data_template = os.getenv('ATF_TEST_DATA_TEMPLATE_PATH')
    if atf_test_data_template is None:
        atf_test_data_template = os.path.join(atf_root_path, 'atf_test', 'data_template')
    atf_config['ATF_TEST_DATA_TEMPLATE_PATH'] = atf_test_data_template

    # Define test dir
    atf_test_path = os.getenv('ATF_TEST_PATH')
    if atf_test_path is None:
        atf_test_path = os.path.join(atf_root_path, 'atf_test')
    atf_config['ATF_TEST_PATH'] = atf_test_path
    if not os.path.exists(atf_test_path):
        os.mkdir(atf_test_path)

    # Define test case dir
    atf_test_case_path = os.getenv('ATF_TEST_CASE_PATH')
    if atf_test_case_path is None:
        atf_test_case_path = os.path.join(atf_root_path, 'atf_test', 'case')
    atf_config['ATF_TEST_CASE_PATH'] = atf_test_case_path

    # Define test data dir
    atf_test_data_path = os.getenv('ATF_TEST_DATA_PATH')
    if atf_test_data_path is None:
        atf_test_data_path = os.path.join(atf_root_path, 'atf_test', 'data')
    atf_config['ATF_TEST_DATA_PATH'] = atf_test_data_path

    # Define test output dir
    atf_test_output_path = os.getenv('ATF_TEST_OUTPUT_PATH')
    if atf_test_output_path is None:
        atf_test_output_path = os.path.join(atf_root_path, 'atf_output')
    atf_config['ATF_TEST_OUTPUT_PATH'] = atf_test_output_path

    # Define test scripts dir
    atf_test_scripts_path = os.getenv('ATF_TEST_SCRIPTS_PATH')
    if atf_test_scripts_path is None:
        atf_test_scripts_path = os.path.join(atf_root_path, 'atf_test', 'scripts')
    atf_config['ATF_TEST_SCRIPTS_PATH'] = atf_test_scripts_path

    # Define test variables dir
    atf_test_variables_path = os.getenv('ATF_TEST_VARIABLES_PATH')
    if atf_test_variables_path is None:
        atf_test_variables_path = os.path.join(atf_root_path, 'atf_test', 'variables')
    atf_config['ATF_TEST_VARIABLES_PATH'] = atf_test_variables_path

    # Check dirs
    for dir_path in atf_config.values():
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    # # Define test env
    # atf_config['ATF_TEST_ENV'] = dict()
    # for _env_key in os.environ:
    #     if str(_env_key).startswith('ATF_TEST_ENV_'):
    #         atf_config['ATF_TEST_ENV'][_env_key] = os.getenv(_env_key)
    # if atf_config['ATF_TEST_ENV'].get('ATF_TEST_ENV_ACCESS_URL') is None:
    #     atf_config['ATF_TEST_ENV']['ATF_TEST_ENV_ACCESS_URL'] = 'http://127.0.0.1'

    # Generate config YAML
    with open(os.path.join(atf_config_path, 'config.yaml'), 'w') as config_file:
        config_file.write(yaml.safe_dump(atf_config))

    # Generate test variables YAML
    _var_init = {
        'ACCESS_URL': 'http://127.0.0.1',
        'ACCOUNT': 'user',
        'PASSWORD': 'password',
    }
    with open(os.path.join(atf_test_variables_path, 'variables.yaml'), 'w') as variables_file:
        variables_file.write(yaml.safe_dump(_var_init))

    # Return variables
    logging.info('Init complete')
    return atf_config


def load_atf_config():
    logging.info('Try to load ATF config')
    atf_config_file = os.path.join('atf_config', 'config.yaml')
    if os.path.exists(atf_config_file):
        with open(atf_config_file, 'r') as f:
            atf_variables = yaml.full_load(f.read())
        for atf_var_key in atf_variables:
            if os.getenv(atf_var_key) is None:
                os.environ[atf_var_key] = atf_variables.get(atf_var_key)
        logging.info('Loading complete')
    else:
        logging.info('No ATF config can be found')


def main():
    if len(sys.argv) == 1:
        help_doc()
    if sys.argv[1] == 'init':
        logging.info('API Testing Framework ---- Init ---- Start')
        atf_var = init_atf_config()
        code_gen = CodeGenerator()
        with open(os.path.join(atf_var['ATF_TEST_SCRIPTS_PATH'], 'setupSuite.py'), 'w') as script_file:
            script_file.write(code_gen.new_setup_suite())
        with open(os.path.join(atf_var['ATF_TEST_SCRIPTS_PATH'], 'teardownSuite.py'), 'w') as script_file:
            script_file.write(code_gen.new_teardown_suite())
        with open(os.path.join(atf_var['ATF_TEST_SCRIPTS_PATH'], 'setupCase.py'), 'w') as script_file:
            script_file.write(code_gen.new_setup_case())
        with open(os.path.join(atf_var['ATF_TEST_SCRIPTS_PATH'], 'teardownCase.py'), 'w') as script_file:
            script_file.write(code_gen.new_teardown_case())
        logging.info('API Testing Framework ---- Init ---- Finished')
    elif sys.argv[1] == 'prepare':
        logging.info('API Testing Framework ---- Prepare ---- Start')
        load_atf_config()
        # atf_var = init_atf_config()
        sp = SwaggerParser()
        for _doc in sp.api_doc_list:
            sp.parse_doc(doc_file_name=_doc)
        logging.info('API Testing Framework ---- Prepare ---- Finished')
    elif sys.argv[1] == 'run':
        logging.info('API Testing Framework ---- Run ---- Start')
        # atf_var = init_prepare_for_atf()
        load_atf_config()
        sys.path.append(os.getenv('ATF_TEST_SCRIPTS_PATH'))
        try:
            _args = sys.argv[2]
        except IndexError:
            _args = ''
        _html_report = os.path.join(os.getenv('ATF_TEST_OUTPUT_PATH'), 'report.html')
        pytest.main([
            '-v',
            '-r chars',
            '--color=yes',
            '--html=%s' % _html_report,
            '--capture=no',
            # '--setup-show',
            # '--show-capture=all',
            _args
        ])
        logging.info('API Testing Framework ---- Run ---- Finished')
    elif sys.argv[1] == 'clean':
        logging.info('API Testing Framework ---- Clean ---- Start')
        load_atf_config()
        rm_dir_list = [
            os.getenv('ATF_TEST_CASE_PATH'),
            # os.getenv('ATF_TEST_DATA_PATH'),
            os.getenv('ATF_TEST_DATA_TEMPLATE_PATH')
        ]
        for _dir in rm_dir_list:
            logging.info('Cleanup ext dir: %s' % _dir)
            subprocess.getoutput('rm -rf %s' % _dir)
            # os.mkdir(_dir)
        # logging.info('Cleanup ext dir: tests/test_env')
        # subprocess.getoutput('cd tests && rm -rf test_env && cp -R test_env_template test_env')
        logging.info('API Testing Framework ---- Clean ---- Finished')
    else:
        help_doc()
