"""Scan endpoints — upload, status polling, WebSocket progress, background scan."""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)

from models.scan import ScanProgress, ScanResult, ScanStatus

logger = logging.getLogger("stegaguard.scan")

router = APIRouter(tags=["scan"])

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
UPLOAD_DIR = Path("/tmp/stegaguard")
ALLOWED_EXTENSIONS = {".safetensors", ".pt", ".onnx", ".pth"}

scans: dict[str, ScanResult] = {}
progress_queues: dict[str, asyncio.Queue] = {}


# ---------------------------------------------------------------------------
# POST /api/scan — accept model file and kick off background analysis
# ---------------------------------------------------------------------------
@router.post("/scan")
async def start_scan(file: UploadFile):
    # Validate extension
    ext = _file_extension(file.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    scan_id = str(uuid.uuid4())

    # Persist uploaded file to disk
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / f"{scan_id}{ext}"
    try:
        contents = await file.read()
        file_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}")

    # Initialise scan record
    scans[scan_id] = ScanResult(scan_id=scan_id, status=ScanStatus.PENDING)

    # Create progress queue before launching the task so that any WS
    # connection established immediately after this response can receive
    # events from the very beginning.
    progress_queues[scan_id] = asyncio.Queue()

    # Fire-and-forget background scan
    asyncio.create_task(_run_scan(scan_id, str(file_path), file.filename or ""))

    return {"scan_id": scan_id}


# ---------------------------------------------------------------------------
# GET /api/scan/{scan_id} — poll current scan state
# ---------------------------------------------------------------------------
@router.get("/scan/{scan_id}")
async def get_scan(scan_id: str):
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans[scan_id]


# ---------------------------------------------------------------------------
# WS /api/scan/{scan_id}/ws — real-time progress stream
# ---------------------------------------------------------------------------
@router.websocket("/scan/{scan_id}/ws")
async def scan_ws(websocket: WebSocket, scan_id: str):
    await websocket.accept()

    if scan_id not in scans:
        await websocket.send_json({"error": "Scan not found"})
        await websocket.close(code=1008)
        return

    # Ensure a queue exists (it normally does, but guard against late connects)
    if scan_id not in progress_queues:
        progress_queues[scan_id] = asyncio.Queue()

    queue = progress_queues[scan_id]

    try:
        while True:
            event: Optional[ScanProgress] = await queue.get()
            if event is None:
                # None sentinel signals scan completion — send final result
                if scan_id in scans:
                    await websocket.send_json(scans[scan_id].model_dump(mode="json"))
                break
            await websocket.send_json(event.model_dump(mode="json"))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected for scan %s", scan_id)
    except Exception:
        logger.exception("WebSocket error for scan %s", scan_id)
    finally:
        await websocket.close()


# ---------------------------------------------------------------------------
# Background scan
# ---------------------------------------------------------------------------
async def _run_scan(scan_id: str, file_path: str, filename: str):
    """Execute the full scan pipeline in the background."""
    from core.parser import parse_model
    from core.scanner import run_scan

    scans[scan_id].status = ScanStatus.RUNNING

    async def on_progress(progress: ScanProgress):
        if scan_id in progress_queues:
            await progress_queues[scan_id].put(progress)

    try:
        weights, metadata = parse_model(file_path)
        metadata.filename = filename
        result = await run_scan(weights, metadata, progress_callback=on_progress)
        result.scan_id = scan_id
        result.status = ScanStatus.COMPLETED
        scans[scan_id] = result
    except Exception as exc:
        logger.exception("Scan %s failed", scan_id)
        scans[scan_id].status = ScanStatus.FAILED
        scans[scan_id].error = str(exc)
    finally:
        # Signal WS consumers that the scan has finished
        if scan_id in progress_queues:
            await progress_queues[scan_id].put(None)
        # Clean up the temp file
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError:
                logger.warning("Could not remove temp file %s", file_path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _file_extension(filename: str) -> str:
    """Return the lowered file extension including the dot."""
    _, ext = os.path.splitext(filename)
    return ext.lower()
