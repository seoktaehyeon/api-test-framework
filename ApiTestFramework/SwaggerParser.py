#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import yaml
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, urljoin
from ApiTestFramework.CodeGenerator import CodeGenerator


class SwaggerParser(object):
    def __init__(self):
        with open(os.path.join('atf_config', 'config.yaml'), 'r') as f:
            self.config = yaml.full_load(f.read())
        with open(os.path.join(self.config['ATF_TEST_VARIABLES_PATH'], 'variables.yaml'), 'r') as f:
            self.variables = yaml.full_load(f.read())
        self.api_doc_dir = self.config['ATF_API_DOC_PATH']
        self.test_data_template_dir = self.config['ATF_TEST_DATA_TEMPLATE_PATH']
        self.test_case_dir = self.config['ATF_TEST_CASE_PATH']
        self.api_doc_list = os.listdir(self.api_doc_dir)

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
        _base_url = {
            'scheme': '',
            'netloc': '',
            'path': '',
        }
        try:
            _base_url_obj = urlparse(_doc_content['servers'][0]['url'])
            _base_url['scheme'] = _base_url_obj.scheme
            _base_url['netloc'] = _base_url_obj.netloc
            _base_url['path'] = _base_url_obj.path
        except KeyError:
            _base_url_obj = ''
        if self.variables.get('ACCESS_URL'):
            _base_url_obj = urlparse(self.variables.get('ACCESS_URL'))
            _base_url['scheme'] = _base_url_obj.scheme
            _base_url['netloc'] = _base_url_obj.netloc
        _base_url_str = urljoin(
            base=_base_url.get('scheme') + '://' + _base_url.get('netloc'),
            url=_base_url.get('path')
        )
        logging.info('Base URL: %s' % _base_url_str)
        logging.info(u'解析文档中的 paths')
        for _path_url, _methods in _doc_content['paths'].items():
            logging.info(u'获取接口 %s 的 method 和具体内容' % _path_url)
            for _method, _detail in _methods.items():
                if _method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'head']:
                    continue
                _parameters = {
                    'path': dict(),
                    'header': dict(),
                    'query': dict(),
                    'body': dict(),
                }
                logging.info(u'解析文档中 %s %s 接口的 parameters' % (_method, _path_url))
                if _detail.get('parameters') is not None:
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
                    _response_content_detail = _response_content_detail.get('content')
                except TypeError:
                    _response_content_detail = dict()
                if _response_content_detail.get('type') == 'array':
                    _response_content = dict()
                    for _key, _value in _response_content_detail['items']['properties'].items():
                        _response_content[_key] = _value.get('type') + ' # %s' % _value.get('description')
                else:
                    _response_content = dict()
                _api = {
                    'summary': _detail.get('summary'),
                    'method': _method.lower(),
                    'url': _base_url_str + _path_url.lower(),
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
                    if not _api.get('summary'):
                        _api['summary'] = _test_data_file_name[:-5]
                    yaml.safe_dump(_api, f, allow_unicode=True, sort_keys=False)

                logging.info(u'生成测试用例内容')
                _test_case_title = '%s %s' % (_method.upper(), _base_url_str + _path_url.lower())
                _test_case_content = CodeGenerator.append_test_case(
                    case_content=_test_case_content,
                    test_function=_test_data_file_name.split('.yaml')[0],
                    test_suite=_suite,
                    test_case=_test_data_file_name,
                    test_case_title=_test_case_title
                )
                # _test_case_content = '\n'.join([
                #     _test_case_content,
                #     '    def test_%s(self):' % _test_data_file_name.split('.yaml')[0],
                #     '        self.ce.get_test_case_requests(',
                #     '            test_suite=\'%s\',' % _suite,
                #     '            test_case=\'%s\',' % _test_data_file_name,
                #     '            test_case_title=\'%s\'' % _test_case_title,
                #     '        )',
                #     '        for test_request_data in self.ce.test_requests_data:',
                #     '            self.ce.exec_test_case(test_request_data)',
                #     '',
                # ])
        _test_case_suite = os.path.join(self.test_case_dir, 'test_' + _suite + '.py')
        if os.path.exists(_test_case_suite):
            _test_case_suite = os.path.join(
                self.test_case_dir,
                'test_' + _suite + '_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.py'
            )
        logging.info(u'生成测试用例套件 %s' % _test_case_suite)
        _test_case_suite_content = CodeGenerator.new_test_suite(
            suite_name=_suite.capitalize(),
            case_content=_test_case_content
        )
        # '\n'.join([
        #     '#!/usr/local/env python3',
        #     '# -*- coding: utf-8 -*-',
        #     '',
        #     'from ApiTestFramework.CaseExecutor import CaseExecutor',
        #     '',
        #     '',
        #     'class Test%s(object):' % _suite.capitalize(),
        #     '',
        #     '    def setup_class(self):',
        #     '        self.ce = CaseExecutor()',
        #     '        self.ce.setup_class()',
        #     '',
        #     '    def teardown_class(self):',
        #     '        self.ce.teardown_class()',
        #     '',
        #     '    def setup_method(self):',
        #     '        self.ce.setup_method()',
        #     '',
        #     '    def teardown_method(self):',
        #     '        self.ce.teardown_method()',
        #     _test_case_content
        # ])
        with open(_test_case_suite, 'w', encoding='utf-8') as f:
            f.write(_test_case_suite_content)


if __name__ == '__main__':
    print('This is Swagger YAML File parser module')
