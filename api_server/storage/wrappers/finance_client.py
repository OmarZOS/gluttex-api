

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from constants import FINANCE_SERVER_URL
from core.models.finance_models import DailyPaymentStats, InvoicePaymentSummary, PaymentCreate, PaymentRefund, PaymentResponse

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import logging
from datetime import datetime

from core.models.finance_models import (
    DailyPaymentStats, 
    InvoicePaymentSummary, 
    PaymentCreate, 
    PaymentRefund, 
    PaymentResponse,
    PaymentConfirm,
    ErrorResponse
)
from communication.communication_broker import (
    send_post_request,
    send_get_request,
    send_put_request,
    send_delete_request
)

logger = logging.getLogger(__name__)


class FinanceServiceClient:
    """Client for Finance API"""
    
    base_url = FINANCE_SERVER_URL
    timeout = 30  # Default timeout in seconds
    
    async def create_payment(self, payment_data: PaymentCreate) -> PaymentResponse:
        """
        Create a new payment with pending status.
        The invoice must already exist.
        
        Args:
            payment_data: Payment creation data
            
        Returns:
            PaymentResponse: Created payment details
            
        Raises:
            Exception: If the API request fails
        """
        try:
            endpoint = f"{self.base_url}/payments/payment"
            
            # Convert payment data to dict
            request_data = payment_data.model_dump(exclude_none=True)
            
            logger.info(f"Creating payment for invoice {payment_data.invoice_id}")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") in [200, 201]:
                return PaymentResponse(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Payment creation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            raise
    
    async def confirm_payment(self, payment_id: int, transaction_details: Dict) -> PaymentResponse:
        """
        Confirm a pending payment.
        This creates money transactions for wallet transfers.
        
        Args:
            payment_id: ID of the payment to confirm
            transaction_details: Transaction details from payment gateway
            
        Returns:
            PaymentResponse: Confirmed payment details
        """
        try:
            endpoint = f"{self.base_url}/payments/confirm/{payment_id}"
            
            request_data = {
                "transaction_details": transaction_details or {}
            }
            
            logger.info(f"Confirming payment {payment_id}")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return PaymentResponse(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Payment confirmation failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to confirm payment {payment_id}: {e}")
            raise
    
    async def reject_payment(self, payment_id: int, reason: str) -> PaymentResponse:
        """
        Reject a pending payment.
        No transactions are created.
        
        Args:
            payment_id: ID of the payment to reject
            reason: Reason for rejection
            
        Returns:
            PaymentResponse: Rejected payment details
        """
        try:
            endpoint = f"{self.base_url}/payments/reject/{payment_id}"
            
            request_data = {"reason": reason}
            
            logger.info(f"Rejecting payment {payment_id} - Reason: {reason}")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return PaymentResponse(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Payment rejection failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to reject payment {payment_id}: {e}")
            raise
    
    async def get_invoice_payments(self, invoice_id: int) -> InvoicePaymentSummary:
        """
        Get all payments for an invoice.
        
        Args:
            invoice_id: ID of the invoice
            
        Returns:
            InvoicePaymentSummary: Summary of payments for the invoice
        """
        try:
            endpoint = f"{self.base_url}/payments/invoice/{invoice_id}"
            
            logger.info(f"Getting payments for invoice {invoice_id}")
            
            response = await send_get_request(
                endpoint=endpoint,
                params={}
            )
            
            if response.get("status_code") == 200:
                return InvoicePaymentSummary(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Failed to get invoice payments: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to get payments for invoice {invoice_id}: {e}")
            raise
    
    async def get_payment(self, payment_id: int) -> PaymentResponse:
        """
        Get payment details with transactions.
        
        Args:
            payment_id: ID of the payment
            
        Returns:
            PaymentResponse: Payment details
        """
        try:
            endpoint = f"{self.base_url}/payments/{payment_id}"
            
            logger.info(f"Getting payment {payment_id}")
            
            response = await send_get_request(
                endpoint=endpoint,
                params={}
            )
            
            if response.get("status_code") == 200:
                return PaymentResponse(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Failed to get payment details: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to get payment {payment_id}: {e}")
            raise
    
    async def refund_payment(self, payment_id: int, refund_data: PaymentRefund) -> PaymentResponse:
        """
        Refund a completed payment.
        Creates reverse transactions.
        
        Args:
            payment_id: ID of the payment to refund
            refund_data: Refund data including amount and reason
            
        Returns:
            PaymentResponse: Refunded payment details
        """
        try:
            endpoint = f"{self.base_url}/payments/refund/{payment_id}"
            
            request_data = refund_data.model_dump(exclude_none=True)
            
            logger.info(f"Refunding payment {payment_id} - Amount: {refund_data.amount}")
            
            response = await send_post_request(
                endpoint=endpoint,
                json_data=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.get("status_code") == 200:
                return PaymentResponse(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Refund failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to refund payment {payment_id}: {e}")
            raise
    
    async def get_daily_stats(self, date: Optional[str] = None) -> DailyPaymentStats:
        """
        Get daily payment statistics.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            DailyPaymentStats: Daily payment statistics
        """
        try:
            endpoint = f"{self.base_url}/payments/stats/daily"
            
            params = {}
            if date:
                params["date"] = date
            else:
                # Default to today
                params["date"] = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"Getting daily stats for {params.get('date')}")
            
            response = await send_get_request(
                endpoint=endpoint,
                params=params
            )
            
            if response.get("status_code") == 200:
                return DailyPaymentStats(**response.get("data", {}))
            else:
                error_msg = response.get("data", {}).get("detail", "Unknown error")
                raise Exception(f"Failed to get daily stats: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to get daily stats: {e}")
            raise
    
    async def health_check(self) -> Dict[str, str]:
        """
        Check the health of the Finance API.
        
        Returns:
            Dict: Health status
        """
        try:
            endpoint = f"{self.base_url}/payments/health"
            
            response = await send_get_request(
                endpoint=endpoint,
                params={}
            )
            
            if response.get("status_code") == 200:
                return response.get("data", {"status": "healthy"})
            else:
                return {"status": "unhealthy", "error": response.get("data", {}).get("detail", "Unknown error")}
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

