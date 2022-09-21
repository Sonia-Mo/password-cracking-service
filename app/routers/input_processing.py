from fastapi import APIRouter, UploadFile, File
from app import intervals
from app.exceptions import InvalidInputException
import hashlib
import time
from typing import Set
import ray

router = APIRouter()
output = {}

# Start Ray.
ray.init()


@ray.remote
def check_interval(hash_str, range_start, range_end):
    for i in range(range_start, range_end):
        result = hashlib.md5(f"0{i}".encode()).hexdigest()
        if result == hash_str:
            return True, f"0{i}"
    return False, None


def validate_input_file():
    pass


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
    content = await file.read()
    hash_lst = content.split(b'\r\n')

    # validate_input_file()

    start = time.time()
    for password_hash in hash_lst:
        password_hash = password_hash.decode()
        output[password_hash] = crack_hash(password_hash)
    end = time.time()

    return (end - start), output

