from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from app.schemas.base import BaseSchema

class QualityCheckIssue(BaseSchema):
    issue_id: str
    description: str
    severity: str = Field(description="Severity of the issue, e.g., 'low', 'medium', 'high'")
    timestamp: datetime

class QualityCheckResponse(BaseSchema):
    user_id: str
    issues: List[QualityCheckIssue]
    total_issues: int
    timestamp: datetime