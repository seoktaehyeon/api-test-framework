# Mini API Test Framework
> It is not smart, just a hard worker.
 
```text
.
├── ApiTestFramework
│   ├── CaseExecutor.py
│   ├── CodeGenerator.py
│   ├── SwaggerParser.py
│   └── __init__.py
├── Dockerfile
├── README.md
├── atf-exec
├── docker-compose.yaml
├── requirements.txt
└── setup.py
```

## Installation
```bash
git clone https://github.com/seoktaehyeon/api-test-framework.git
cd api-test-framework
./setup.py install
```

## Usage
```text
Usage: atf-exec <command>
command:
    init    Init framework
    prepare Generate test case in test_case dir and data template in data_template dir
    run     Run test case
    clean   Cleanup workspace
```

## Quick Start
```bash
# 1. Install ATF
git clone https://github.com/seoktaehyeon/api-test-framework.git
cd api-test-framework
./setup.py install
# 2. Init ATF
mkdir api_test
cd api_test
atf-exec init
# 3. Put swagger YAML into atf_api_docs
wget http://xxxx/xxx.yaml -O atf_api_docs/xxx.yaml 
# 4. Prepare for running
atf-exec prepare
# 5. Add test data into atf_test/data refer to atf_test/data_template
# 6. Execute testing
atf-exec run
```
