import subprocess
from google.protobuf.message import Message

def read(filename: str, reader: Message) -> Message:
    print(f"reading: {filename}")
    
    # download the data
    result = subprocess.run(["ipfs", "files", "read", "/data/" + filename], capture_output=True)

    # parse the data
    data = result.stdout
    print(f"read bytes: {data}")
    reader.ParseFromString(data)
    return reader

def write(filename: str, data: Message) -> None:
    print(f"writing: {filename}")

    # write data to a local file
    filepath = "src/generated/tmp/" + filename
    with open(filepath, "wb") as f:
        # serialize the data before writing
        print(f"writing bytes: {data.SerializeToString()}")
        f.write(data.SerializeToString())

    # upload that file
    p = subprocess.run(["ipfs", "add", filepath, "--to-files", "/data/"], capture_output=True)
    print(p.stdout)

    # remove the temporary file
    subprocess.run(["rm", filepath])
