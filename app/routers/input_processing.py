from fastapi import APIRouter, UploadFile, File
from app import intervals
from app.exceptions import InvalidInputException
import hashlib
import time
from typing import Set
import ray
import re

router = APIRouter()
output = {}

# Start Ray.
ray.init()


async def prepare_and_validate_input(file):
    content = await file.read()

    if content.decode() == "":
        raise InvalidInputException.empty_file

    hash_lst = content.split(b'\r\n')
    for i, password_hash in enumerate(hash_lst):
        decoded_hash = password_hash.decode()
        # MD5 hashes are always a string of 32 characters composed of letters and numbers
        if not re.search("^[0-9a-fA-F]{32}$", decoded_hash):
            raise InvalidInputException.not_MD5_hash
        hash_lst[i] = decoded_hash

    return hash_lst


@ray.remote
def check_interval(hash_str, range_start, range_end):
    for i in range(range_start, range_end):
        result = hashlib.md5(f"0{i}".encode()).hexdigest()
        if result == hash_str:
            return True, f"0{i}"
    return False, None


def process_results(results: Set[tuple]):
    # If only (False, None) exists in set, then hash is not cracked
    if len(results) == 1:
        raise InvalidInputException.not_phone_number

    for (found, password) in results:
        if found:
            return password


def crack_hash(password_hash):
    result = []
    for (interval_start, interval_end) in intervals:
        # Use Ray functionality to distribute work between workers
        result.append(check_interval.remote(password_hash, interval_start, interval_end))
    return process_results(set(ray.get(result)))


@router.post("/upload-file/")
async def upload_hash_file(file: UploadFile = File(...)):
    hash_lst = await prepare_and_validate_input(file)

    start = time.time()
    for password_hash in hash_lst:
        output[password_hash] = crack_hash(password_hash)
    end = time.time()

    return (end - start), output

