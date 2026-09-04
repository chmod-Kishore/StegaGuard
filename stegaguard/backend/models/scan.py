from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import uuid, datetime

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RiskVerdict(str, Enum):
    CLEAR = "CLEAR"
    LOW = "LOW"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class LayerResult(BaseModel):
    name: str
    param_count: int
    entropy: float = 0.0
    lsb_entropy: float = 0.0
    chi2_statistic: float = 0.0
    chi2_p_value: float = 1.0
    flip_ratio: float = 0.5
    ks_statistic: float = 0.0
    ks_p_value: float = 1.0
    kurtosis: float = 0.0
    entropy_anomaly: bool = False
    lsb_anomaly: bool = False
    distribution_anomaly: bool = False
    status: str = "normal"  # "normal", "warning", "critical"

class ModelMetadata(BaseModel):
    filename: str
    format: str  # "safetensors", "pytorch", "onnx"
    file_size_bytes: int
    total_params: int
    layer_count: int
    file_hash: str = ""

class RiskBreakdown(BaseModel):
    max_entropy_score: float = 0.0
    max_lsb_score: float = 0.0
    max_distribution_score: float = 0.0
    mean_entropy_score: float = 0.0
    metadata_score: float = 0.0

class ScanResult(BaseModel):
    scan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: ScanStatus = ScanStatus.PENDING
    metadata: Optional[ModelMetadata] = None
    risk_score: float = 0.0
    verdict: RiskVerdict = RiskVerdict.CLEAR
    risk_breakdown: Optional[RiskBreakdown] = None
    layer_results: list[LayerResult] = []
    summary: str = ""
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    error: Optional[str] = None

class ScanProgress(BaseModel):
    scan_id: str
    stage: str  # "parsing", "entropy", "lsb", "distribution", "scoring"
    layer: str = ""
    progress: float = 0.0  # 0.0 to 1.0
    message: str = ""
