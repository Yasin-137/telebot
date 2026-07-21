import httpx
from config import Config


class ZarinPal:
    def __init__(self):
        self.merchant_id = Config.ZARINPAL_MERCHANT_ID
        self.callback_url = Config.ZARINPAL_CALLBACK_URL
        self.sandbox = Config.ZARINPAL_SANDBOX
        self.api_base = Config.ZARINPAL_SANDBOX_API if self.sandbox else Config.ZARINPAL_API

    async def create_payment(self, amount: int, description: str, email: str = None,
                             mobile: str = None) -> dict:
        """Create a payment request. Amount should be in Rials."""
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": self.callback_url,
            "description": description,
        }
        if email:
            payload["email"] = email
        if mobile:
            payload["mobile"] = mobile

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/payment/request.json",
                json=payload,
                timeout=30
            )
            data = response.json()

        if data.get("data", {}).get("code") == 100:
            authority = data["data"]["authority"]
            gateway_url = (
                f"https://sandbox.zarinpal.com/pg/StartPay/{authority}"
                if self.sandbox
                else f"https://www.zarinpal.com/pg/StartPay/{authority}"
            )
            return {
                "success": True,
                "authority": authority,
                "gateway_url": gateway_url
            }
        return {
            "success": False,
            "error": data.get("errors", {}).get("message", "خطا در ایجاد پرداخت")
        }

    async def verify_payment(self, authority: str, amount: int) -> dict:
        """Verify a payment after redirect."""
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/payment/verify.json",
                json=payload,
                timeout=30
            )
            data = response.json()

        code = data.get("data", {}).get("code")
        if code in (100, 101):
            return {
                "success": True,
                "ref_id": data["data"].get("ref_id"),
                "card_pan": data["data"].get("card_pan"),
                "message": "پرداخت با موفقیت انجام شد"
            }
        return {
            "success": False,
            "error": data.get("errors", {}).get("message", "خطا در تایید پرداخت")
        }


zarinpal = ZarinPal()
