# API Test Framework
```text
.
├── Dockerfile
├── README.md
├── api-tester.py
├── data_template
├── openapi_docs
│   └── README.md
├── requirements.txt
├── test_case
├── test_data
├── test_env
│   ├── __init__.py
│   ├── scripts
│   │   └── __init__.py
│   └── variables.py
└── utils
    ├── CaseExecutor.py
    ├── SwaggerParser.py
    └── __init__.py
```
## Setup Test Bed
#### git clone
#### docker
#### docker-compose YAML
```yaml
version: '3'
services:
  api-test-framework:
    image: bxwill/api-test-framework:stable
    container_name: api-test-framework
    restart: always
    volumes:
      - ./atf/test_case:/workspace/test_case
      - ./atf/test_data:/workspace/test_data
      - ./atf/data_template:/workspace/data_template
      - ./atf/test_env:/workspace/test_env
    environment:
      TEST_SERVER_URL: http://api-test-framework
      TEST_ACCOUNT: tester
      TEST_PASSWORD: password
```

## Usage
```bash
Usage: ./api-tester.py option
option:
    init    Init test case and generate data template in data_template dir
    run     Run test case
    clean   Clean up workspace
```
