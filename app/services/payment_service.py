import hashlib
import base64
import json
import uuid
import httpx
from app.core.config import settings

class PhonePeService:
    """
    PhonePe Payment Gateway Integration.
    
    Flow:
    1. We initiate a payment → PhonePe returns a payment URL
    2. User is redirected to PhonePe to complete payment
    3. PhonePe calls our webhook with the result
    4. We verify the payment and update the order
    """

    def __init__(self):
        self.merchant_id = settings.PHONEPE_MERCHANT_ID
        self.salt_key = settings.PHONEPE_SALT_KEY
        self.salt_index = settings.PHONEPE_SALT_INDEX
        self.base_url = settings.PHONEPE_BASE_URL

    def _generate_checksum(self, payload_base64: str, endpoint: str) -> str:
        """
        PhonePe requires a SHA256 checksum for every request.
        Formula: SHA256(base64_payload + endpoint + salt_key) + "###" + salt_index
        """
        data = payload_base64 + endpoint + self.salt_key
        sha256_hash = hashlib.sha256(data.encode()).hexdigest()
        return f"{sha256_hash}###{self.salt_index}"

    def initiate_payment(self, amount_inr: float, user_id: int, merchant_txn_id: str) -> dict:
        """
        Initiate a PhonePe payment.
        Returns: { success, payment_url, merchant_transaction_id }
        """
        amount_paisa = int(amount_inr * 100)  # Convert INR to paisa

        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": merchant_txn_id,
            "merchantUserId": f"USER_{user_id}",
            "amount": amount_paisa,
            "redirectUrl": settings.PHONEPE_REDIRECT_URL,
            "redirectMode": "POST",
            "callbackUrl": settings.PHONEPE_CALLBACK_URL,
            "paymentInstrument": {
                "type": "PAY_PAGE"  # Redirect user to PhonePe payment page
            }
        }

        # Encode payload to base64
        payload_json = json.dumps(payload)
        payload_base64 = base64.b64encode(payload_json.encode()).decode()

        endpoint = "/pg/v1/pay"
        checksum = self._generate_checksum(payload_base64, endpoint)

        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
        }

        request_body = {"request": payload_base64}

        try:
            response = httpx.post(
                f"{self.base_url}{endpoint}",
                json=request_body,
                headers=headers,
                timeout=30.0
            )
            data = response.json()

            if data.get("success") and data.get("code") == "PAYMENT_INITIATED":
                payment_url = data["data"]["instrumentResponse"]["redirectInfo"]["url"]
                return {
                    "success": True,
                    "payment_url": payment_url,
                    "merchant_transaction_id": merchant_txn_id,
                }
            else:
                return {"success": False, "error": data.get("message", "Payment initiation failed")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_payment(self, merchant_txn_id: str) -> dict:
        """
        Verify payment status with PhonePe.
        Call this after receiving webhook or callback.
        Returns: { success, status, phonepe_transaction_id }
        """
        endpoint = f"/pg/v1/status/{self.merchant_id}/{merchant_txn_id}"
        checksum = self._generate_checksum("", endpoint)

        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
            "X-MERCHANT-ID": self.merchant_id,
        }

        try:
            response = httpx.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                timeout=30.0
            )
            data = response.json()

            if data.get("success") and data.get("code") == "PAYMENT_SUCCESS":
                return {
                    "success": True,
                    "status": "SUCCESS",
                    "phonepe_transaction_id": data["data"].get("transactionId"),
                }
            else:
                return {
                    "success": False,
                    "status": data.get("code", "PAYMENT_FAILED"),
                    "phonepe_transaction_id": None,
                }
        except Exception as e:
            return {"success": False, "status": "ERROR", "error": str(e)}

    def verify_webhook_checksum(self, response_base64: str, received_checksum: str) -> bool:
        """Verify that the webhook actually came from PhonePe."""
        data = response_base64 + self.salt_key
        expected = hashlib.sha256(data.encode()).hexdigest() + f"###{self.salt_index}"
        return expected == received_checksum


# Singleton instance
phonepe_service = PhonePeService()
