# ipfs (interplanetary filesystem) kvs (key value store)

## Run tests
To only run tests: `pytest`  

To run all checks: `nox`

## Regenerate pb2.py files
`protoc --python_out=. --proto_path=protobuf protobuf/sample.proto`
