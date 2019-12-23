#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class CodeGenerator(object):
    def __init__(self):
        pass

    @staticmethod
    def new_test_suite(suite_name, case_content):
        return '\n'.join([
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '',
            'from ApiTestFramework.CaseExecutor import CaseExecutor',
            '',
            '',
            'class Test%s(object):' % suite_name,
            '',
            '    def setup_class(self):',
            '        self.ce = CaseExecutor()',
            '        self.ce.setup_class()',
            '',
            '    def teardown_class(self):',
            '        self.ce.teardown_class()',
            '',
            '    def setup_method(self):',
            '        self.ce.setup_method()',
            '',
            '    def teardown_method(self):',
            '        self.ce.teardown_method()',
            case_content
        ])

    @staticmethod
    def append_test_case(case_content, test_function, test_suite, test_case, test_case_title):
        return '\n'.join([
            case_content,
            '    def test_%s(self):' % test_function,
            '        self.ce.get_test_case_requests(',
            '            test_suite=\'%s\',' % test_suite,
            '            test_case=\'%s\',' % test_case,
            '            test_case_title=\'%s\'' % test_case_title,
            '        )',
            '        for test_request_data in self.ce.test_requests_data:',
            '            self.ce.exec_test_case(test_request_data)',
            '',
        ])

    @staticmethod
    def _setup_teardown(script_name):
        return '\n'.join([
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '',
            '',
            'def run(test_env: dict):',
            '    # This is a %s script' % script_name,
            '    pass',
            ''
        ])

    def new_setup_suite(self):
        return self._setup_teardown('suite Setup')

    def new_teardown_suite(self):
        return self._setup_teardown('suite TearDown')

    def new_setup_case(self):
        return self._setup_teardown('case Setup')

    def new_teardown_case(self):
        return self._setup_teardown('case TearDown')
