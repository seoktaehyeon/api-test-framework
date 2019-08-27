# Mini API Test Framework
```text
.
├── Dockerfile
├── README.md
├── api-tester.py
├── docker-compose.yaml
├── openapi_docs
│   └── README.md
├── requirements.txt
├── tests
│   ├── __init__.py
│   ├── data_template
│   ├── test_case
│   ├── test_data
│   ├── test_env
│   │   ├── __init__.py
│   │   ├── scripts
│   │   │   └── __init__.py
│   │   └── variables.py
│   └── test_env_template
│       ├── __init__.py
│       ├── scripts
│       │   └── __init__.py
│       └── variables.py
└── utils
    ├── CaseExecutor.py
    ├── SwaggerParser.py
    └── __init__.py
```

## Usage
```bash
Usage: ./api-tester.py option
option:
    init    Init test case and generate data template in data_template dir
    run     Run test case
    clean   Clean up workspace
```

## How To Run In Test Bed

#### Option I: git 
```bash
# Download code
git clone 
# Put swagger YAML into openapi_docs
wget http://xxxx/xxx.yaml -O openapi_docs/xxx.yaml or mv xxx.yaml openapi_docs/xxx.yaml
# After init, you will find data_template/test_case in your test bed
./api-tester.py init
# Copy data_template into test_data and modify them ready to test
./api-tester.py run
```
#### Option II: docker
```bash
docker-compose -f compose.yaml up -d
```
compose.yaml content as bellow:
```yaml
version: '3'
services:
  api-test-framework:
    image: bxwill/api-test-framework:stable
    container_name: api-test-framework
    restart: always
    volumes:
      - ./atf/openapi_docs:/workspace/openapi_docs
      - ./atf/test_case:/workspace/tests/test_case
      - ./atf/test_data:/workspace/tests/test_data
      - ./atf/data_template:/workspace/tests/data_template
      - ./atf/test_env:/workspace/tests/test_env
    environment:
      TEST_SERVER_URL: <http://api-test-framework>
      TEST_ACCOUNT: <tester>
      TEST_PASSWORD: <password>
```
```bash
# Except git clone, there only ./api-tester.py execution method is different with Option I
docker exec -it api-test-framework ./api-tester.py init
docker exec -it api-test-framework ./api-tester.py run
```

