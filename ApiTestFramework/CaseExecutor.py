#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import yaml
import logging
import pytest
from urllib.parse import urlparse, urljoin
import json


class CaseExecutor(object):
    def __init__(self):
        with open(os.path.join('atf_config', 'config.yaml'), 'r') as f:
            self.config = yaml.full_load(f.read())
        with open(os.path.join(self.config['ATF_TEST_VARIABLES_PATH'], 'variables.yaml'), 'r') as f:
            self.variables = yaml.full_load(f.read())
        self.test_requests_data = list()

    def show_env(self):
        _envs = list()
        _max_len = len(max(self.variables.keys(), key=len))
        for _key, _value in self.variables.items():
            _blank = ' ' * (_max_len - len(_key))
            _envs.append('  %s%s: %s' % (_key, _blank, _value))
        return '\n'.join(_envs)

    def setup_class(self):
        logging.info('Setup Suite for Testing')
        try:
            module = __import__('%s.scripts.setupSuite' % self.config['ATF_TEST_PATH'], fromlist=True)
            module.run(self.variables)
        except ModuleNotFoundError:
            logging.info('No operation during setup suite')

    def teardown_class(self):
        logging.info('Teardown Suite for Testing')
        try:
            module = __import__('%s.scripts.teardownSuite' % self.config['ATF_TEST_PATH'], fromlist=True)
            module.run(self.variables)
        except ModuleNotFoundError:
            logging.info('No operation during teardown suite')

    def setup_method(self):
        logging.info('Setup Case for Testing')
        try:
            module = __import__('%s.scripts.setupCase' % self.config['ATF_TEST_PATH'], fromlist=True)
            module.run(self.variables)
        except ModuleNotFoundError:
            logging.info('No operation during setup case')
        logging.info('ENV:\n%s' % self.show_env())

    def teardown_method(self):
        logging.info('Teardown Case for Testing')
        try:
            module = __import__('%s.scripts.teardownCase' % self.config['ATF_TEST_PATH'], fromlist=True)
            module.run(self.variables)
        except ModuleNotFoundError:
            logging.info('No operation during teardown case')

    def get_test_case_requests(self, test_suite: str, test_case: str, test_case_title: str):
        logging.info(u'测试接口: %s' % test_case_title)

        logging.info(u'测试 %s 中的 %s' % (test_suite, test_case))
        _requests_data = list()
        _file_path = os.path.join(self.config['ATF_TEST_DATA_PATH'], test_suite, test_case)
        if os.path.exists(_file_path) is False:
            pytest.skip(u'缺少测试数据文件')

        logging.info(u'获取 %s 中的数据' % _file_path)
        with open(_file_path, 'r') as f:
            _content = yaml.full_load(f.read())
        logging.debug(_content)
        _origin_url = urlparse(_content.get('url'))
        _test_url = urlparse(self.variables.get('ACCESS_URL'))
        _url = urljoin(
            base=_test_url.scheme + '://' + _test_url.netloc,
            url=_origin_url.path
        )

        for _key in _content.keys():
            if _key not in ['summary', 'method', 'url', 'template']:
                logging.debug(u'获取 %s 的数据' % _key)
                _test_request_data = {
                    'scenario': _key,
                    'method': _content.get('method'),
                    'url': _url
                }
                for _content_key, _content_value in _content[_key].items():
                    _test_request_data[_content_key] = _content_value
                    logging.debug(u'%s: %s' % (_content_key, _content_value))
                _requests_data.append(_test_request_data)

        if len(_requests_data) == 0:
            pytest.skip(u'缺少可用的测试数据')
        self.test_requests_data = _requests_data
        return True

    def _replace_value(self, items):
        if isinstance(items, dict):
            for key, value in items.items():
                if isinstance(value, str):
                    if value.startswith('{') and value.endswith('}'):
                        items[key] = self.variables.get(value[1:-1])
                        logging.info(u'%s 是变量%s, 替换成 %s' % (key, value, items[key]))
                    elif value.startswith('${') and value.endswith('}'):
                        module = __import__(
                            '%s.scripts.%s' % (self.config['ATF_TEST_PATH'], value[2:-1]),
                            fromlist=True
                        )
                        items[key] = module.run(self.variables)
                        logging.info(u'%s 是函数%s, 替换成 %s' % (key, value, items[key]))
        return items

    def _generate_parameters(self, test_request_data):
        # URL
        _url = test_request_data['url']
        _path = test_request_data['path']
        self._replace_value(_path)
        for _key, _value in _path.items():
            _url = _url.replace('{%s}' % _key, _value)
        # Headers
        _headers = test_request_data['header'] if test_request_data['header'] is not None else {}
        _headers['Accept'] = 'application/json'
        _headers['Content-Type'] = 'application/json'
        _headers = self._replace_value(_headers)
        # Query
        _query = test_request_data['query']
        if _query == {}:
            _query = None
        _query = self._replace_value(_query)
        # Body
        _body = test_request_data['body']
        if _body == {}:
            _body = None
        _body = self._replace_value(_body)
        # Response
        _expected_status_code = test_request_data['expectedStatusCode']
        _expected_response = test_request_data['expectedResponse']

        _parameters = {
            'method': test_request_data['method'],
            'url': _url,
            'query': _query,
            'header': _headers,
            'body': _body,
            'expectedStatusCode': _expected_status_code,
            'expectedResponse': _expected_response,
        }
        logging.info(_parameters)
        return _parameters

    @staticmethod
    def _generate_curl(test_request_data):
        # Generate url
        _url = test_request_data['url']
        if test_request_data['query'] is not None:
            _query_list = list()
            for _key, _value in test_request_data['query'].items():
                if _value is None:
                    continue
                _query_list.append('%s=%s' % (_key, _value))
                # _query = '&'.join([
                #     _query,
                #     '%s=%s' % (_key, _value)
                # ])
            if len(_query_list) != 0:
                _query = '&'.join(_query_list)
                _url = _url + '?' + _query
        # Generate headers
        _headers = ''
        for _key, _value in test_request_data['header'].items():
            if _value is None:
                continue
            _headers = ''.join([
                _headers,
                ' -H "%s:%s"' % (_key, _value)
            ])
        # Generate body
        if test_request_data['body'] is None or test_request_data['body'] == {}:
            _body = ''
        else:
            _body = '-d \'%s\'' % json.dumps(test_request_data['body'])
        # Generate CURL
        _curl = ' '.join([
            'curl -s -v -X %s' % test_request_data['method'].upper(),
            _headers,
            _body,
            _url
        ])
        logging.info(_curl)
        return True

    @staticmethod
    def _check_status_code(expected, actual):
        logging.info(u'检查状态码 [预期]%s [实际]%s' % (expected, actual.status_code))
        if actual.status_code == 500:
            logging.error(u'状态码 500 Error')
            raise AssertionError(u'状态码不符合预期')
        elif actual.status_code != expected:
            logging.error(u'状态码不符合预期')
            raise AssertionError(u'状态码不符合预期')
        # assert actual.status_code != 500, u'状态码 500 Error'
        # assert expected == actual.status_code, u'状态码不符合预期'
        return True

    def _check_response(self, expected, actual):
        if expected is not None and expected != {} and expected != []:
            logging.info(u'检查返回值 [预期]%s [实际]%s' % (expected, actual.content.decode('utf-8')))
            expected = self._replace_value(expected)
            try:
                _response = actual.json()
                if isinstance(_response, list) is True:
                    # expected = expected[0]
                    _response = _response[0]
                for _key, _value in expected.items():
                    if _value is None:
                        logging.info('Only check %s in response since %s is None' % (_key, _key))
                        assert _key in _response.keys()
                    else:
                        logging.info(u'返回值 %s [预期]%s [实际]%s' % (_key, _value, _response[_key]))
                        assert _value == _response[_key]
            except AttributeError:
                _response = actual.content.decode('utf-8')
                logging.info('Search %s from response' % expected)
                assert expected in _response
        return True

    def exec_test_case(self, test_request_data: dict):
        logging.info(u'进行接口验证: %s' % test_request_data['scenario'])
        _data = self._generate_parameters(test_request_data)
        self._generate_curl(_data)
        _session = requests.session()
        try:
            _response = _session.request(
                method=test_request_data['method'],
                url=_data['url'],
                params=_data['query'],
                headers=_data['header'],
                json=_data['body'],
                timeout=6
            )
            logging.info('Status Code: %s' % _response.status_code)
            logging.info('Response Content:\n%s' % _response.text)
            self._check_status_code(
                expected=_data['expectedStatusCode'],
                actual=_response
            )
            self._check_response(
                expected=_data['expectedResponse'],
                actual=_response
            )
        except requests.exceptions.ConnectTimeout:
            raise TimeoutError(u'请求超时')
        finally:
            _session.close()


if __name__ == '__main__':
    print('This is a class for Case Execution')
