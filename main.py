from src.ipfs import Ipfs

# Ipfs().does_file_exist(filename="test_directory123")

ipfs = Ipfs()

# Define the expected directory name
directory_name = "test_directory"

# Call the mkdir() function with the expected directory name
ipfs.mkdir(directory_name)

# Assert that the subprocess was called with the expected command
assert ipfs.does_file_exist(directory_name)

# Cleanup: delete the directory
# ipfs.delete(directory_name)