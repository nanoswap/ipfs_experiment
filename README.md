# ipfs (interplanetary filesystem) kvs (key value store)

## Run tests
To only run tests: `pytest`  

To run all checks: `nox`

## Regenerate pb2.py files
```
cd protobuf;
protoc --python_out=../proto --proto_path=protobuf protobuf/sample.proto
```
