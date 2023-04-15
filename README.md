# ipfs (interplanetary filesystem) kvs (key value store)

## Build docs
`mkdocs serve`

## Run tests
To only run tests: `pytest`  
To run all checks: `nox`

Note: before running tests:
   - Generate the pb2.py files used for testing
   - Make sure your local ipfs daemon is running

## Regenerate pb2.py files
```
cd protobuf;
protoc --python_out=../proto --proto_path=protobuf protobuf/sample.proto
```

## Run the ipfs daemon
```
ipfs daemon --api /ip4/0.0.0.0/tcp/5001
```
Check the status of your node at:
  - http://localhost:5001/webui
  - https://webui.ipfs.io/#/status

### ipfs setup
https://docs.ipfs.tech/install/

### ipfs troubleshooting

Set the log level, send the logs to a file, and search the file for relevant messages
```
export IPFS_LOGGING=<debug|info|error>
ipfs daemon --debug 2>&1 | tee ipfs.log
cat ipfs.log | grep test_directory
```

If you find something important, you can show the first few lines around that message
```
grep -C 10 '2023-04-13T17:31:49.712-0400' ipfs.log
```

Here is an example of an error message in these logs:
```
2023-04-13T17:31:49.712-0400	DEBUG	cmds/http	http/handler.go:90	incoming API request: /files/mkdir?arg=test_directory
2023-04-13T17:31:49.712-0400	DEBUG	cmds	go-ipfs-cmds@v0.8.2/command.go:161	error occured in call, closing with error: paths must start with a leading slash
```
