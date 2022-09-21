from fastapi import FastAPI
from app import intervals
from app.routers.input_processing import router

app = FastAPI()
app.include_router(router)

INTERVAL_SIZE = 1000000  # TODO: move to settings file?


@app.on_event("startup")
async def create_intervals():
    interval_start = 500000000
    interval_end = interval_start + INTERVAL_SIZE
    while interval_end < 600000000:
        intervals.append((interval_start, interval_end))
        interval_start = interval_end
        interval_end += INTERVAL_SIZE
    intervals.append((interval_start, 600000000))
    return
