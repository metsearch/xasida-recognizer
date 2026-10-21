import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.api import index, recognize, references, versions, xasidas
from src.database.qdrant import ensure_collection, get_client


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_collection(get_client())
    yield


app = FastAPI(title="Xasida Recognizer", lifespan=lifespan)

app.include_router(xasidas.router)
app.include_router(references.router)
app.include_router(versions.router)
app.include_router(index.router)
app.include_router(recognize.router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
