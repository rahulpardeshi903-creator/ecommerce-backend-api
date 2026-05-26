import uuid
import base64
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.schemas.payment import PaymentInitiate, PaymentResponse
from app.models.payment import Payment, PaymentStatus
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.services.payment_service import phonepe_service

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/initiate", response_model=PaymentResponse)
def initiate_payment(
    data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Initiate PhonePe payment for an order."""
    order = db.query(Order).filter(
        Order.id == data.order_id,
        Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order is not in a payable state")

    # Generate unique transaction ID
    merchant_txn_id = f"TXN_{current_user.id}_{order.id}_{uuid.uuid4().hex[:8].upper()}"

    # Call PhonePe API
    result = phonepe_service.initiate_payment(
        amount_inr=order.total_amount,
        user_id=current_user.id,
        merchant_txn_id=merchant_txn_id
    )

    if not result["success"]:
        raise HTTPException(status_code=502, detail=f"Payment gateway error: {result.get('error')}")

    # Save payment record
    payment = Payment(
        user_id=current_user.id,
        amount=order.total_amount,
        amount_paisa=int(order.total_amount * 100),
        status=PaymentStatus.INITIATED,
        merchant_transaction_id=merchant_txn_id,
        payment_url=result["payment_url"],
    )
    db.add(payment)
    db.flush()

    # Link payment to order
    order.payment_id = payment.id
    db.commit()
    db.refresh(payment)

    return payment

@router.post("/webhook")
async def phonepe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    PhonePe calls this URL after payment is completed.
    This is the server-to-server callback.
    """
    body = await request.json()
    response_base64 = body.get("response", "")
    received_checksum = request.headers.get("X-VERIFY", "")

    # Verify the webhook came from PhonePe
    if not phonepe_service.verify_webhook_checksum(response_base64, received_checksum):
        raise HTTPException(status_code=400, detail="Invalid checksum")

    # Decode the response
    decoded = json.loads(base64.b64decode(response_base64).decode())
    merchant_txn_id = decoded.get("data", {}).get("merchantTransactionId")

    if not merchant_txn_id:
        return {"status": "ignored"}

    payment = db.query(Payment).filter(Payment.merchant_transaction_id == merchant_txn_id).first()
    if not payment:
        return {"status": "payment not found"}

    # Verify with PhonePe API (double-check)
    verification = phonepe_service.verify_payment(merchant_txn_id)

    if verification["success"] and verification["status"] == "SUCCESS":
        payment.status = PaymentStatus.SUCCESS
        payment.phonepe_transaction_id = verification.get("phonepe_transaction_id")

        # Update order status
        if payment.order:
            payment.order.status = OrderStatus.CONFIRMED
    else:
        payment.status = PaymentStatus.FAILED

    db.commit()
    return {"status": "processed"}

@router.get("/callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    User is redirected here after completing payment on PhonePe.
    This is the browser redirect (user-facing).
    """
    from fastapi.responses import RedirectResponse
    from app.core.config import settings

    params = dict(request.query_params)
    merchant_txn_id = params.get("transactionId")

    if merchant_txn_id:
        payment = db.query(Payment).filter(Payment.merchant_transaction_id == merchant_txn_id).first()
        if payment and payment.status == PaymentStatus.SUCCESS:
            return RedirectResponse(f"{settings.FRONTEND_URL}/order/success?txn={merchant_txn_id}")

    return RedirectResponse(f"{settings.FRONTEND_URL}/order/failed")

@router.get("/{merchant_txn_id}/status", response_model=PaymentResponse)
def check_payment_status(
    merchant_txn_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check payment status for a transaction."""
    payment = db.query(Payment).filter(
        Payment.merchant_transaction_id == merchant_txn_id,
        Payment.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
