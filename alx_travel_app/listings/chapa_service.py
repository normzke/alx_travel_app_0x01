import os
import requests
import logging
from django.conf import settings
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ChapaService:
    """Service class for handling Chapa API operations"""
    
    def __init__(self):
        self.secret_key = os.getenv('CHAPA_SECRET_KEY')
        self.base_url = 'https://api.chapa.co/v1'
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initiate_payment(self, booking, amount: float, currency: str = 'USD') -> Dict:
        """
        Initiate a payment with Chapa API
        
        Args:
            booking: Booking instance
            amount: Payment amount
            currency: Payment currency (default: USD)
            
        Returns:
            Dict containing payment response from Chapa
        """
        try:
            # Calculate number of nights
            nights = (booking.check_out - booking.check_in).days
            
            payload = {
                'amount': str(amount),
                'currency': currency,
                'email': booking.user.email,
                'first_name': booking.user.first_name or booking.user.username,
                'last_name': booking.user.last_name or '',
                'tx_ref': f"booking_{booking.id}_{booking.user.id}",
                'callback_url': f"{settings.BASE_URL}/api/payments/verify/",
                'return_url': f"{settings.BASE_URL}/api/payments/success/",
                'customization': {
                    'title': f'Payment for {booking.listing.title}',
                    'description': f'Booking for {nights} nights at {booking.listing.title}'
                }
            }
            
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Payment initiated successfully for booking {booking.id}")
                return {
                    'success': True,
                    'data': data,
                    'payment_url': data.get('data', {}).get('checkout_url'),
                    'reference': data.get('data', {}).get('reference')
                }
            else:
                logger.error(f"Failed to initiate payment: {response.text}")
                return {
                    'success': False,
                    'error': f"Chapa API error: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return {
                'success': False,
                'error': f"Payment initiation failed: {str(e)}"
            }
    
    def verify_payment(self, reference: str) -> Dict:
        """
        Verify payment status with Chapa API
        
        Args:
            reference: Chapa transaction reference
            
        Returns:
            Dict containing verification response
        """
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Payment verification successful for reference {reference}")
                return {
                    'success': True,
                    'data': data,
                    'status': data.get('data', {}).get('status')
                }
            else:
                logger.error(f"Failed to verify payment: {response.text}")
                return {
                    'success': False,
                    'error': f"Verification failed: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return {
                'success': False,
                'error': f"Payment verification failed: {str(e)}"
            }
    
    def get_payment_status(self, reference: str) -> Optional[str]:
        """
        Get payment status from Chapa
        
        Args:
            reference: Chapa transaction reference
            
        Returns:
            Payment status string or None if failed
        """
        result = self.verify_payment(reference)
        if result['success']:
            return result.get('status')
        return None 