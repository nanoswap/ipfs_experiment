import subprocess
from google.protobuf.message import Message

def read(filename: str, reader: Message) -> Message:
    """
    Read a file from ipfs

    Args:
        filename (str): The file to read
        reader (Message): The protobuf schema to deserialize the file contents

    Returns:
        Message: A protobuf object containing the file contents
    """
    # download the data
    result = subprocess.run(["ipfs", "files", "read", "/data/" + filename], capture_output=True)

    # parse the data
    data = result.stdout
    reader.ParseFromString(data)
    return reader

def write(filename: str, data: Message) -> None:
    """
    Create a new file in ipfs.
    This does not work for updating existing files.

    Args:
        filename (str): The filename for the uploaded data
        data (Message): The protobuf object that will be written to the new file
    """
    # write data to a local file
    filepath = "src/generated/tmp/" + filename
    with open(filepath, "wb") as f:
        # serialize the data before writing
        f.write(data.SerializeToString())

    # upload that file
    subprocess.run(["ipfs", "add", filepath, "--to-files", "/data/"], capture_output=True)
 
    # remove the temporary file
    subprocess.run(["rm", filepath])
