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
    def exec_test_case(test_request_data):
        logging.info(u'进行接口验证: %s' % test_request_data['scenario'])
        _session = requests.session()
        _url = test_request_data['url']
        _path = test_request_data['path']
        _headers = test_request_data['header']
        _headers['Accept'] = 'application/json'
        _headers['Content-Type'] = 'application/json'
        _query = test_request_data['query']
        _body = test_request_data['body']
        _expected_status_code = test_request_data['expectedStatusCode']
        _expected_response = test_request_data['expectedResponse']
        try:
            _response = _session.request(
                method=test_request_data['method'],
                url=_url,
                params=_query,
                headers=_headers,
                json=_body
            )
            logging.info(_response.status_code)
            logging.info(_response.text)
            logging.info(u'检查状态码')
            assert _response.status_code == _expected_status_code, \
                u'状态码不符合预期: [预期]%s [实际]%s' % (_expected_status_code, _response.status_code)
        finally:
            _session.close()
            # raise AssertionError(u'请求失败')
