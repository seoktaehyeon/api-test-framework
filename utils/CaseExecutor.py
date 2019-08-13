#! /usr/local/env python3
# -*- coding: utf-8 -*-

import os
import requests
import yaml
import logging


class CaseExecutor(object):
    def __init__(self):
        self.test_data_dir = os.path.join('test_data')
        self.test_requests_data = list()

    # def get_test_suites(self):
    #     return os.listdir(self.test_data_dir)
    #
    # def get_test_cases(self, test_suite: str):
    #     _test_suite_dir = os.path.join(self.test_data_dir, test_suite)
    #     return os.listdir(_test_suite_dir)

    def get_test_case_requests(self, test_suite: str, test_case: str):
        logging.info(u'测试 %s 中的 %s' % (test_suite, test_case))
        _requests_data = list()
        _file_path = os.path.join(self.test_data_dir, test_suite, test_case)
        logging.info(u'获取 %s 中的数据' % _file_path)
        with open(_file_path, 'r') as f:
            _content = yaml.full_load(f.read())
        logging.info(_content)
        for _key in _content.keys():
            if _key != 'summary' and _key != 'template':
                logging.debug(u'获取 %s 的数据' % _key)
                _test_request_data = {
                    'scenario': _key
                }
                for _content_items in _content[_key]:
                    for _content_key, _content_value in _content_items.items():
                        _test_request_data[_content_key] = _content_value
                        logging.debug(u'%s: %s' % (_content_key, _content_value))
                _requests_data.append(_test_request_data)
        self.test_requests_data = _requests_data
        return True

    @staticmethod
    def _generate_parameters(test_request_data):
        # URL
        _url = test_request_data['url']
        _path = test_request_data['path']
        for _key, _value in _path.items():
            _url = _url.replace('{%s}' % _key, _value)
        # Headers
        _headers = test_request_data['header']
        _headers['Accept'] = 'application/json'
        _headers['Content-Type'] = 'application/json'
        # Query
        _query = test_request_data['query']
        if _query == {}:
            _query = None
        # Body
        _body = test_request_data['body']
        if _body == {}:
            _body = None
        # Response
        _expected_status_code = test_request_data['expectedStatusCode']
        _expected_response = test_request_data['expectedResponse']

        return {
            'method': test_request_data['method'],
            'url': _url,
            'query': _query,
            'header': _headers,
            'body': _body,
            'expectedStatusCode': _expected_status_code,
            'expectedResponse': _expected_response,
        }

    @staticmethod
    def _generate_curl(test_request_data):
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
            _query = '&'.join(_query_list)
            _url = _url + '?' + _query
        _headers = ''
        for _key, _value in test_request_data['header'].items():
            if _value is None:
                continue
            _headers = ''.join([
                _headers,
                ' -H "%s:%s"' % (_key, _value)
            ])
        if test_request_data['body'] is None:
            _body = ''
        else:
            _body = test_request_data['body']
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
        assert expected == actual.status_code, u'状态码不符合预期'
        return True

    @staticmethod
    def _check_response(expected, actual):
        if expected is not None and expected != {} and expected != []:
            logging.info(u'检查返回值 [预期]%s [实际]%s' % (expected, actual.content.decode('utf-8')))
            try:
                _response = actual.json()
                if isinstance(_response, list) is True:
                    expected = expected[0]
                    _response = _response[0]
                for _key, _value in expected.items():
                    if _value is None:
                        logging.info('Only check %s in response since %s is None' % (_key, _key))
                        assert _key in _response.keys()
                    else:
                        logging.info(u'返回值 [预期]%s [实际]%s' % (_value, _response[_key]))
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
                timeout=10
            )
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
