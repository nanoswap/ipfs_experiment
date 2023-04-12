import subprocess
from src import utils

def test_mkdir():
    """ Test that a directory can be created """

    # make the directory
    directory_name = 'test_mkdir_dir'
    utils.mkdir(f"/{directory_name}")

    # check that it was created
    output = subprocess.run(['ipfs', 'files', 'ls'], capture_output=True)
    assert directory_name in output.stdout.decode()

    # cleanup - delete the test directory
    subprocess.run(['ipfs', 'files', 'rm', '-r', directory_name])
