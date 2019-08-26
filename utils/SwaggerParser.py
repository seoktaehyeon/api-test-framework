#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import yaml
import os
import logging


class SwaggerParser(object):
    def __init__(self):
        self.api_doc_dir = os.path.join('openapi_docs')
        self.test_data_template_dir = os.path.join('data_template')
        self.test_case_dir = os.path.join('test_case')
        self.api_doc_list = os.listdir(self.api_doc_dir)
        self.api_doc_list.remove('README.md')

    def parse_doc(self, doc_file_name: str):
        logging.info(u'获取接口文档名作为 suite name')
        _suite = doc_file_name.split('.yaml')[0]
        logging.info('Suite Name: %s' % _suite)
        logging.info(u'拼接接口文档的路径')
        _doc_file_path = os.path.join(self.api_doc_dir, doc_file_name)
        logging.info('API Doc File Path: %s' % _doc_file_path)
        logging.info(u'读取接口文档的内容')
        _test_case_content = ''
        with open(_doc_file_path, 'r') as f:
            _doc_content = yaml.full_load(f.read())
        logging.info(u'获取文档中 servers 下的 url 作为基础路径')
        _base_url = _doc_content['servers'][0]['url']
        # if os.getenv('TEST_SERVER_URL'):
        #     _base_url = urljoin(os.getenv('TEST_SERVER_URL'), urlparse(_base_url).path)
        logging.info('Base URL: %s' % _base_url)
        logging.info(u'解析文档中的 paths')
        for _path_url, _methods in _doc_content['paths'].items():
            logging.info(u'获取接口 %s 的 method 和具体内容' % _path_url)
            for _method, _detail in _methods.items():
                _parameters = {
                    'path': dict(),
                    'header': dict(),
                    'query': dict(),
                    'body': dict(),
                }
                logging.info(u'解析文档中接口的 parameters')
                for _parameter in _detail['parameters']:
                    logging.debug(u'parameter 可能存在于 path, header, query, body')
                    _parameters[_parameter['in']][_parameter['name']] = ''.join([
                        _parameter['schema']['type'],
                        ' * ' if _parameter.get('required') else '',
                        ' # ',
                        _parameter.get('description') if _parameter.get('description') else '',
                        ' default: %s' % _parameter.get('default') if _parameter.get('default') else '',
                        ' maximum: %s' % _parameter.get('maximum') if _parameter.get('maximum') else '',
                    ])
                logging.info(u'定义接口数据用例模板的内容')
                _status_code = 200
                _response_content_detail = _detail['responses'].get(_status_code)
                if _response_content_detail is None:
                    _response_content_detail = _detail['responses'].get(str(_status_code))
                try:
                    _response_content_detail = _response_content_detail['content']['application/json']['schema']
                except KeyError:
                    _response_content_detail = _response_content_detail['content']
                if _response_content_detail.get('type') == 'array':
                    _response_content = dict()
                    for _key, _value in _response_content_detail['items']['properties'].items():
                        _response_content[_key] = _value.get('type') + ' # %s' % _value.get('description')
                else:
                    _response_content = dict()
                _api = {
                    'summary': _detail.get('summary'),
                    'method': _method.lower(),
                    'url': _base_url + _path_url.lower(),
                    'template': {
                        'path': _parameters['path'],
                        'header': _parameters['header'],
                        'query': _parameters['query'],
                        'body': _parameters['body'],
                        'expectedStatusCode': _status_code,
                        'expectedResponse': _response_content,
                    }
                }
                logging.info(u'定义测试数据套件路径，suite name %s 作为套件名称' % _suite)
                _test_data_suite_path = os.path.join(
                    self.test_data_template_dir,
                    _suite
                )
                logging.info(u'检查套件是否存在，不存在就创建')
                if os.path.exists(_test_data_suite_path) is False:
                    logging.info('Create dir %s since it does not exist' % _test_data_suite_path)
                    os.makedirs(_test_data_suite_path)
                logging.debug(u'定义测试数据文件路径，method + path 作为文件名，并替换掉 / 和 {}')
                _test_data_file_name = ''.join([
                    _method.lower(),
                    _path_url.lower(),
                    '.yaml'
                ]).replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')
                _test_data_file_path = os.path.join(
                    _test_data_suite_path,
                    _test_data_file_name
                )
                logging.info(u'把解析后的接口内容写入 YAML 格式的测试数据文件 %s' % _test_data_file_path)
                with open(_test_data_file_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(_api, f, allow_unicode=True, sort_keys=False)

                logging.info(u'生成测试用例内容')
                _test_case_content = '\n'.join([
                    _test_case_content,
                    '    def test_%s(self):' % _test_data_file_name.split('.yaml')[0],
                    '        ce = CaseExecutor()',
                    '        ce.get_test_case_requests(',
                    '            test_suite=\'%s\',' % _suite,
                    '            test_case=\'%s\'' % _test_data_file_name,
                    '        )',
                    '        for test_request_data in ce.test_requests_data:',
                    '            ce.exec_test_case(test_request_data)',
                    '',
                ])
            _test_case_suite = os.path.join(self.test_case_dir, 'test_' + _suite + '.py')
            logging.info(u'生成测试用例套件 %s' % _test_case_suite)
            _test_case_suite_content = '\n'.join([
                '#!/usr/local/env python3',
                '# -*- coding: utf-8 -*-',
                '',
                'from utils.CaseExecutor import CaseExecutor',
                '',
                '',
                'class Test%s(object):' % _suite.capitalize(),
                _test_case_content
            ])
            with open(_test_case_suite, 'w', encoding='utf-8') as f:
                f.write(_test_case_suite_content)


if __name__ == '__main__':
    print('This is Swagger YAML File parser module')
