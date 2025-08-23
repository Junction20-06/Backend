from pydantic import BaseModel
from typing import List

class NodeReport(BaseModel):
    node_id: int
    status: str

class ReportOut(BaseModel):
    strengths: List[NodeReport]
    weaknesses: List[NodeReport]
    neutrals: List[NodeReport]

