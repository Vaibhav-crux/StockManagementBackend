from datetime import datetime, timezone
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.purchased_orders import PurchasedOrders
from app.schemas.quality_check import QualityCheckIssue, QualityCheckResponse
from app.middleware.logger import get_logger

# Initialize logger for tracking service activity
logger = get_logger()

async def perform_quality_checks(db: AsyncSession, user_id: uuid.UUID) -> QualityCheckResponse:
    """
    Perform quality checks on the user's orders and return flagged issues.
    """
    logger.info(f"Performing quality checks for user_id={user_id}")

    # Fetch all purchased orders for the given user
    result = await db.execute(select(PurchasedOrders).where(PurchasedOrders.user_id == user_id))
    purchased_orders = result.scalars().all()
    
    # If no orders are found, return a 404 error
    if not purchased_orders:
        logger.warning(f"No purchased orders found for user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No purchased orders found for the user",
        )

    issues = []  # List to store detected quality issues
    current_time = datetime.now(timezone.utc)  # Ensure timezone-aware datetime

    for order in purchased_orders:
        # Check 1: Validate that purchase price is a positive value
        if order.purchase_price <= 0:
            issues.append(
                QualityCheckIssue(
                    issue_id=str(uuid.uuid4()),
                    description=f"Invalid purchase price for order_id={order.id}",
                    severity="high",  # High severity since price should always be positive
                    timestamp=current_time,
                )
            )

        # Check 2: Validate that purchase quantity is a positive value
        if order.purchase_qty <= 0:
            issues.append(
                QualityCheckIssue(
                    issue_id=str(uuid.uuid4()),
                    description=f"Invalid purchase quantity for order_id={order.id}",
                    severity="medium",  # Medium severity as it may indicate an input error
                    timestamp=current_time,
                )
            )

        # Check 3: Ensure order timestamp is not in the future
        if order.timestamp > current_time:  # Compare with offset-aware datetime
            issues.append(
                QualityCheckIssue(
                    issue_id=str(uuid.uuid4()),
                    description=f"Invalid timestamp for order_id={order.id}",
                    severity="high",  # High severity as timestamps should always be past or present
                    timestamp=current_time,
                )
            )

    logger.info(f"Found {len(issues)} issues for user_id={user_id}")

    return QualityCheckResponse(
        user_id=str(user_id),
        issues=issues,  # Return list of detected issues
        total_issues=len(issues),  # Total count of flagged issues
        timestamp=current_time,  # Timestamp of quality check execution
    )
