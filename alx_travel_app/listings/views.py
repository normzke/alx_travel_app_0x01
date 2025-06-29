from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .chapa_service import ChapaService
import logging

logger = logging.getLogger(__name__)

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        listing = self.get_object()
        bookings = Booking.objects.filter(listing=listing)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Create payment record for the booking
        self._create_payment_for_booking(booking)

    def _create_payment_for_booking(self, booking):
        """Create a payment record for a booking"""
        try:
            # Calculate total amount based on nights and listing price
            nights = (booking.check_out - booking.check_in).days
            total_amount = booking.listing.price * nights
            
            payment = Payment.objects.create(
                booking=booking,
                amount=total_amount,
                currency='USD'
            )
            logger.info(f"Payment record created for booking {booking.id}")
        except Exception as e:
            logger.error(f"Error creating payment for booking {booking.id}: {str(e)}")

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save()
            return Response({'status': 'booking confirmed'})
        return Response(
            {'error': 'Booking cannot be confirmed'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'cancelled':
            booking.status = 'cancelled'
            booking.save()
            # Update payment status if exists
            if hasattr(booking, 'payment'):
                booking.payment.status = 'cancelled'
                booking.payment.save()
            return Response({'status': 'booking cancelled'})
        return Response(
            {'error': 'Booking is already cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """Initiate payment for a booking using Chapa API"""
        booking = self.get_object()
        
        # Check if payment already exists
        if hasattr(booking, 'payment') and booking.payment.payment_url:
            return Response({
                'message': 'Payment already initiated',
                'payment_url': booking.payment.payment_url,
                'payment_id': str(booking.payment.id)
            })
        
        # Create payment if it doesn't exist
        if not hasattr(booking, 'payment'):
            self._create_payment_for_booking(booking)
        
        # Initiate payment with Chapa
        chapa_service = ChapaService()
        result = chapa_service.initiate_payment(
            booking=booking,
            amount=float(booking.payment.amount),
            currency=booking.payment.currency
        )
        
        if result['success']:
            # Update payment record with Chapa response
            booking.payment.payment_url = result['payment_url']
            booking.payment.chapa_reference = result['reference']
            booking.payment.save()
            
            return Response({
                'message': 'Payment initiated successfully',
                'payment_url': result['payment_url'],
                'payment_id': str(booking.payment.id),
                'reference': result['reference']
            })
        else:
            return Response({
                'error': 'Failed to initiate payment',
                'details': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__user=user)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify payment status from Chapa callback"""
        try:
            reference = request.data.get('reference')
            if not reference:
                return Response({
                    'error': 'Reference is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find payment by reference
            payment = get_object_or_404(Payment, chapa_reference=reference)
            
            # Verify with Chapa API
            chapa_service = ChapaService()
            result = chapa_service.verify_payment(reference)
            
            if result['success']:
                chapa_status = result['status']
                
                # Update payment status based on Chapa response
                if chapa_status == 'success':
                    payment.status = 'completed'
                    payment.save()
                    
                    # Update booking status
                    booking = payment.booking
                    booking.status = 'confirmed'
                    booking.save()
                    
                    # Send confirmation email
                    self._send_confirmation_email(booking)
                    
                    logger.info(f"Payment {payment.id} completed successfully")
                    
                elif chapa_status == 'failed':
                    payment.status = 'failed'
                    payment.save()
                    logger.warning(f"Payment {payment.id} failed")
                
                return Response({
                    'message': 'Payment verification completed',
                    'payment_status': payment.status,
                    'booking_status': payment.booking.status
                })
            else:
                return Response({
                    'error': 'Payment verification failed',
                    'details': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in payment verification: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def success(self, request):
        """Handle successful payment return"""
        reference = request.GET.get('reference')
        if reference:
            payment = get_object_or_404(Payment, chapa_reference=reference)
            return Response({
                'message': 'Payment completed successfully',
                'payment_id': str(payment.id),
                'booking_id': payment.booking.id
            })
        return Response({
            'message': 'Payment completed'
        })

    def _send_confirmation_email(self, booking):
        """Send confirmation email to user"""
        try:
            subject = f'Booking Confirmed - {booking.listing.title}'
            message = f"""
            Dear {booking.user.username},
            
            Your booking has been confirmed!
            
            Booking Details:
            - Property: {booking.listing.title}
            - Check-in: {booking.check_in}
            - Check-out: {booking.check_out}
            - Total Amount: ${booking.payment.amount}
            
            Thank you for choosing our service!
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [booking.user.email],
                fail_silently=True,
            )
            logger.info(f"Confirmation email sent to {booking.user.email}")
        except Exception as e:
            logger.error(f"Error sending confirmation email: {str(e)}")

    @action(detail=True, methods=['post'])
    def check_status(self, request, pk=None):
        """Manually check payment status"""
        payment = self.get_object()
        
        if not payment.chapa_reference:
            return Response({
                'error': 'No Chapa reference found for this payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        chapa_service = ChapaService()
        result = chapa_service.verify_payment(payment.chapa_reference)
        
        if result['success']:
            chapa_status = result['status']
            
            # Update payment status
            if chapa_status == 'success' and payment.status != 'completed':
                payment.status = 'completed'
                payment.save()
                
                # Update booking status
                booking = payment.booking
                booking.status = 'confirmed'
                booking.save()
                
                # Send confirmation email
                self._send_confirmation_email(booking)
            
            return Response({
                'payment_status': payment.status,
                'chapa_status': chapa_status,
                'booking_status': payment.booking.status
            })
        else:
            return Response({
                'error': 'Failed to check payment status',
                'details': result['error']
            }, status=status.HTTP_400_BAD_REQUEST) 