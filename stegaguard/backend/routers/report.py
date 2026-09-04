"""Report endpoint — returns completed scan results formatted as a report."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models.scan import ScanStatus

# The scans dict lives in routers.scan; import it directly.
from routers.scan import scans

router = APIRouter(tags=["report"])


@router.get("/report/{scan_id}")
async def get_report(scan_id: str):
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")

    result = scans[scan_id]

    if result.status != ScanStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Scan is not yet completed (status: {result.status.value})",
        )

    return {
        "scan_id": result.scan_id,
        "verdict": result.verdict,
        "risk_score": result.risk_score,
        "risk_breakdown": result.risk_breakdown,
        "metadata": result.metadata,
        "layer_results": result.layer_results,
        "summary": result.summary,
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }
