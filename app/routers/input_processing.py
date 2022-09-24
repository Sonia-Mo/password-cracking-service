from fastapi import APIRouter, UploadFile, File
from app import intervals
from app.exceptions import InvalidInputException
import hashlib
from typing import Set, List
import ray
from re import search

router = APIRouter()


@router.on_event("startup")
def initialize_ray():
    ray.init()


def prepare_and_validate_input(client_input: UploadFile) -> List[str]:
    """ Verify that the file is applicable using the following criteria:
    (1) file format is txt.  (2) file is not empty.  (3) file contains only MD5 hashes.
    In case file is valid, prepare it for processing by splitting it into a list of hashes.
    """
    if not client_input.filename.endswith('.txt'):
        raise InvalidInputException.wrong_file_format

    with client_input.file as f:
        content = f.read()

    if content.decode() == "":
        raise InvalidInputException.empty_file

    # Prepare list of hashes for processing and convert hashes from bytes to strings
    hash_lst = content.split(b'\r\n')
    hash_lst = [password_hash.decode() for password_hash in hash_lst]

    # MD5 hashes are always a string of 32 characters composed of letters and numbers
    for hash_string in hash_lst:
        if not search("^[0-9a-fA-F]{32}$", hash_string):
            raise InvalidInputException.not_MD5_hash
    return hash_lst


@ray.remote(max_retries=-1)
def check_interval(hash_string: str, interval_start: int, interval_end: int) -> tuple:
    """ The minion servers function - receives hash and a range of potential passwords,
    goes over the range, calculates the hash of each function and compares it to the given hash.
    If the password is found, a tuple of (True, password) is returned, otherwise (False, None).
    """
    for i in range(interval_start, interval_end):
        phone_number_str = f"0{str(i)[:2] + '-' + str(i)[2:]}"
        result = hashlib.md5(phone_number_str.encode()).hexdigest()
        if result == hash_string:
            return True, phone_number_str
    return False, None


def process_results(results: Set[tuple]) -> str:
    """ Receive **set** of results from all minions and arrange the final result.
    For a valid phone number password there should be two tuples: (True, password) and (False, None).
    For invalid password (not a phone number) there should be only (False, None).
    """
    if len(results) == 1:
        raise InvalidInputException.not_phone_number

    for (found, password) in results:
        if found:
            return password


def crack_hash(hash_string: str) -> str:
    """ Manage minions - divide the cracking workload between them using Ray
    functionality to distribute work between workers
    """
    result = []
    for (interval_start, interval_end) in intervals:
        result.append(check_interval.remote(hash_string, interval_start, interval_end))
    return process_results(set(ray.get(result)))


@router.post("/upload-file/")
async def upload_hash_file(client_input: UploadFile = File(...)):
    """ Main endpoint which receives input file and functions as the master server.
    """
    hash_lst = prepare_and_validate_input(client_input)

    output = {}
    for hash_string in hash_lst:
        output[hash_string] = crack_hash(hash_string)

    return output
