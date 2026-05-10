from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from io import BytesIO
import logging
import smtplib
import sys
from tkinter import Image
from venv import logger
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as django_login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import datetime, date
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.uploadedfile import InMemoryUploadedFile
import json
from booking.forms import LoginForm
from .models import DailyEvent, Gallery, Login, Room, RoomType, Booking
from datetime import datetime
from .models import RoomType, Room, Booking, ContactMessage
from .serializers import (
    RoomTypeSerializer,
    RoomSerializer,
    BookingSerializer,
    BookingCreateSerializer,
    ContactMessageSerializer
)
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
logger = logging.getLogger(__name__)
def index(request):
    galleries = Gallery.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'index.html', {'galleries': galleries})

def booking_page(request):
    return render(request, 'booking.html')

@ensure_csrf_cookie
def login_page(request):
    """Render the login page with CSRF token"""
    return render(request, 'login.html')

class RoomTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = [AllowAny]

class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.filter(is_available=True)
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

@api_view(['GET'])
@permission_classes([AllowAny])
def available_rooms(request):
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')
    
    try:
        guests = int(request.GET.get('guests', 1))
    except ValueError:
        return Response({'error': 'Invalid guests value'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    if not check_in_str or not check_out_str:
        return Response({'error': 'Check-in and check-out dates are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        india_tz = ZoneInfo("Asia/Kolkata")

        check_in_datetime = datetime.strptime(
            f"{check_in_str} 12:00 PM",
            "%Y-%m-%d %I:%M %p"
        ).replace(tzinfo=india_tz)

        check_out_datetime = datetime.strptime(
            f"{check_out_str} 11:00 AM",
            "%Y-%m-%d %I:%M %p"
        ).replace(tzinfo=india_tz)
        
     
        if check_in_datetime >= check_out_datetime:
            return Response({'error': 'Check-out date must be after check-in date'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
    
        if check_in_datetime.date() < date.today():
            return Response({'error': 'Check-in date cannot be in the past'}, 
                           status=status.HTTP_400_BAD_REQUEST)

    except ValueError as e:
        return Response({'error': f'Invalid date format. Expected YYYY-MM-DD: {str(e)}'}, 
                       status=status.HTTP_400_BAD_REQUEST)

   
    booked_rooms = Booking.objects.filter(
        check_in_date__lt=check_out_datetime,
        check_out_date__gt=check_in_datetime,
        status__in=['confirmed', 'pending', 'checked_in']
    ).values_list('room_id', flat=True)
    
 
    available_rooms = Room.objects.filter(
        is_available=True,
        room_type__capacity__gte=guests
    ).exclude(id__in=booked_rooms)
    
    serializer = RoomSerializer(available_rooms, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    serializer = BookingCreateSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save()
        
        # Calculate total amount
        check_in = booking.check_in_date
        check_out = booking.check_out_date
        nights = (check_out - check_in).days
        total_amount = booking.room.room_type.price_per_night * nights
        booking.total_amount = total_amount
        booking.save()
        
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_message(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user and user.is_staff:
        django_login(request, user)
        return Response({'message': 'Login successful', 'is_admin': True})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_logout(request):
    logout(request)
    return Response({'message': 'Logout successful'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_bookings(request):
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    bookings = Booking.objects.all()
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_messages(request):
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    messages = ContactMessage.objects.all()
    serializer = ContactMessageSerializer(messages, many=True)
    return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class RoomsAPIView(View):
    def get(self, request):
        """Get all available rooms"""
        try:
            rooms = Room.objects.filter(is_available=True).select_related('room_type')
            rooms_data = []
            for room in rooms:
                rooms_data.append({
                    'id': room.id,
                    'room_number': room.room_number,
                    'floor': room.floor,
                    'is_available': room.is_available,
                    'room_type': {
                        'id': room.room_type.id,
                        'name': room.room_type.name,
                        'description': room.room_type.description,
                        'price_per_night': str(room.room_type.price_per_night),
                        'capacity': room.room_type.capacity,
                        'amenities': room.room_type.amenities,
                        'image': room.room_type.image.url if room.room_type.image else None
                    }
                })
            return JsonResponse(rooms_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class BookingsAPIView(View):
    def post(self, request):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
                file = None
            else:
                data = request.POST
                file = request.FILES.get('customer_id_proof_photo')

            # Validate required fields
            required_fields = ['customer_name', 'customer_email', 'customer_phone', 'room_id']
            for field in required_fields:
                if not data.get(field):
                    print(f"❌ Missing field: {field}")
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            # Get the room
            try:
                room = Room.objects.get(id=data['room_id'], is_available=True)
            except Room.DoesNotExist:
                return JsonResponse({'error': 'Room not found or not available'}, status=404)

            # Parse dates
            india_tz = ZoneInfo("Asia/Kolkata")

            check_in_datetime = datetime.strptime(
                f"{data['check_in_date']} 12:00 PM",
                "%Y-%m-%d %I:%M %p"
            ).replace(tzinfo=india_tz)

            check_out_datetime = datetime.strptime(
                f"{data['check_out_date']} 11:00 AM",
                "%Y-%m-%d %I:%M %p"
            ).replace(tzinfo=india_tz)

        
            if check_in_datetime >= check_out_datetime:
                return JsonResponse({'error': 'Check-out date must be after check-in date'}, status=400)
         
            if check_in_datetime.date() < date.today():
                return JsonResponse({'error': 'Check-in date cannot be in the past'}, status=400)

            # Check availability
            conflicting_bookings = Booking.objects.filter(
                room=room,
                check_in_date__lt=check_out_datetime,
                check_out_date__gt=check_in_datetime,
                status__in=['confirmed', 'pending', 'checked_in']
            )
            if conflicting_bookings.exists():
                return JsonResponse({'error': 'Room is not available for the selected dates'}, status=400)

            # Calculate total
            pure_check_in_date = check_in_datetime.date()
            pure_check_out_date = check_out_datetime.date()
            
            nights = (pure_check_out_date - pure_check_in_date).days
            total_amount = nights * room.room_type.price_per_night
            # Create booking
            booking = Booking.objects.create(
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                customer_phone=data['customer_phone'],
                room=room,
                check_in_date=check_in_datetime,
                check_out_date=check_out_datetime,
                guests=data.get('guests', 1),
                special_requests=data.get('special_requests', ''),
                total_amount=total_amount,
                status='pending',
                customer_id_no=data.get('customer_id_no', ''),
                customer_id_proof_photo=file
            )

            subject = "Booking Confirmation"
            message_body = f"""
            Dear {booking.customer_name},

            Your booking has been successfully created!

            To confirm your booking after payment, please contact us at:
            📞 +91-8233199334  
            📧 gurukultrustrsbd@gmail.com

            Booking Details:
            - Room: {room.room_type.name}
            - Check-in: {check_in_datetime.strftime('%d %B %Y, %I:%M %p')}
            - Check-out: {check_out_datetime.strftime('%d %B %Y, %I:%M %p')}
            - Total Amount: ₹{total_amount}

            Thank you for choosing our service!
            """

            send_email_notification(booking.customer_email, subject, message_body)

            admin_email = "divyeshgandhi2000@gmail.com"
            admin_subject = f"New Booking Alert - {booking.customer_name}"
            admin_message = f"""
            New booking has been created by {booking.customer_name}.

            Please contact the customer to confirm their booking.

            Customer Details:
            - Name: {booking.customer_name}
            - Email: {booking.customer_email}
            - Phone: {booking.customer_phone}
            - Aadhaar No: {booking.customer_id_no}
            - Room: {room.room_type.name}
            - Check-in: {check_in_datetime.strftime('%d %B %Y, %I:%M %p')}
            - Check-out: {check_out_datetime.strftime('%d %B %Y, %I:%M %p')}
            - Total Amount: ₹{total_amount}

            Please follow up with the customer for payment confirmation.
            """

            send_email_notification(admin_email, admin_subject, admin_message)

            return JsonResponse({
                'id': booking.id,
                'message': 'Booking created successfully and confirmation email sent.',
                'total_amount': str(total_amount),
                'nights': nights,
                'booking': {
                    'id': booking.id,
                    'customer_name': booking.customer_name,
                    'total_amount': str(booking.total_amount),
                    'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
                    'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
                    'status': booking.status
                }
            }, status=200)

        except ValueError as e:
            return JsonResponse({'error': f'Invalid date format: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def login_view(request):
    """Fixed login view with proper CSRF handling"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        print(f"Attempting login with Email: {email}")
        
        try:
            login_user = Login.objects.get(email=email)
            print(f"Found user in Login model: {login_user.email}")
            print(f"User role: {login_user.role}")
            print(f"User is_active: {login_user.is_active}")
            if not login_user.is_active:
                print("User is not active")
                messages.error(request, "Your account is not active. Please contact administrator.")
                return render(request, "login.html")
            if login_user.password == password:
                print("Password matches!")
                request.session['user_id'] = login_user.id
                request.session['user_email'] = login_user.email
                request.session['user_role'] = login_user.role
                request.session['is_authenticated'] = True                
                messages.success(request, "Login successful!")
                return redirect('dashboard')
            else:
                print("Password doesn't match")
                messages.error(request, "Invalid Email or Password")
                
        except Login.DoesNotExist:
            print(f"No user found in Login model with email: {email}")
            messages.error(request, "Invalid Email or Password")
        except Exception as e:
            print(f"Error during login: {str(e)}")
            messages.error(request, "An error occurred during login")
    return render(request, "login.html")


def logout_view(request):
    # Clear all session data
    request.session.flush()

    # Prevent browser caching (so back button won't show old pages)
    response = redirect("login_page")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    # Success message
    messages.success(request, "You have been logged out successfully.")
    return response

def is_user_authenticated(request):
    return request.session.get('is_authenticated', False)

def get_current_user(request):
    if not request.session.get('is_authenticated'):
        if request.path.startswith('/api/'):  # <-- NEW CHECK
            return JsonResponse({'error': 'Authentication required'}, status=401)
        # Regular page redirect for non-API
        messages.error(request, "Please log in to access this page.")
        return redirect('login_page')

def custom_login_required(view_func):
    """Modified to handle both API and page requests"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check authentication
        if not request.session.get('is_authenticated'):
            # If it's an API request (starts with /api/), return JSON
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Authentication required',
                    'redirect': '/login/'
                }, status=401)
            # Otherwise, redirect to login page (existing behavior)
            messages.error(request, "Please log in to access this page.")
            return redirect('login_page')
        return view_func(request, *args, **kwargs)
    return wrapper


@custom_login_required
@require_http_methods(["PUT"])
def update_booking_status(request, booking_id):
    current_user = get_current_user(request)
    if not current_user:
        return JsonResponse({'error': 'Authentication required'}, status=401) 
    try:
        booking = Booking.objects.get(id=booking_id)
        data = json.loads(request.body)
        if 'status' in data:
            booking.status = data['status']
            booking.save()
            return JsonResponse({
                'message': 'Booking updated successfully',
                'booking': {
                    'id': booking.id,
                    'status': booking.status
                    
                }
            })
        return JsonResponse({'error': 'Status not provided'}, status=400)
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)




@custom_login_required
@require_http_methods(["POST", "PUT", "DELETE"])
def admin_booking_management(request, booking_id=None):
    """Handle admin booking operations with custom authentication"""
    current_user = get_current_user(request)
    
    if not current_user:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        if request.method == 'POST':
            # Create new booking (similar to BookingsAPIView but with additional validation)
            # data = json.loads(request.body)
            data = request.POST  # gets all text inputs
            file = request.FILES.get('customer_id_proof_photo')  # gets uploaded file

            # Validate required fields
            required_fields = ['customer_name', 'customer_email', 'customer_phone', 'room_id']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            # Get the room
            try:
                room = Room.objects.get(id=data['room_id'], is_available=True)
            except Room.DoesNotExist:
                return JsonResponse({'error': 'Room not found or not available'}, status=404)

            # Parse dates
            check_in_date = datetime.strptime(data['check_in_date'], '%Y-%m-%d').date()
            check_out_date = datetime.strptime(data['check_out_date'], '%Y-%m-%d').date()

            # Calculate total amount
            nights = (check_out_date - check_in_date).days
            total_amount = nights * room.room_type.price_per_night

            # Create booking
            booking = Booking.objects.create(
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                customer_phone=data['customer_phone'],
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                guests=data.get('guests', 1),
                special_requests=data.get('special_requests', ''),
                total_amount=total_amount,
                status=data.get('status', 'pending')
            )

            return JsonResponse({
                'message': 'Booking created successfully',
                'booking': {
                    'id': booking.id,
                    'customer_name': booking.customer_name,
                    'total_amount': str(booking.total_amount),
                    'status': booking.status
                }
            })
        
        elif request.method == 'PUT' and booking_id:
            # Update booking status
            try:
                booking = Booking.objects.get(id=booking_id)
                data = json.loads(request.body)
                
                if 'status' in data:
                    booking.status = data['status']
                    booking.save()
                
                return JsonResponse({
                    'message': 'Booking updated successfully',
                    'booking': {
                        'id': booking.id,
                        'status': booking.status
                    }
                })
            except Booking.DoesNotExist:
                return JsonResponse({'error': 'Booking not found'}, status=404)
        
        elif request.method == 'DELETE' and booking_id:
            # Delete booking
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.delete()
                return JsonResponse({'message': 'Booking deleted successfully'})
            except Booking.DoesNotExist:
                return JsonResponse({'error': 'Booking not found'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)



@custom_login_required
@custom_login_required
@custom_login_required
def dashboard(request):
    current_user = get_current_user(request)
    
    from django.db.models import Sum, Count
    from datetime import datetime, timedelta
    
    # Basic Stats
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status="pending").count()
    confirmed_bookings = Booking.objects.filter(status="confirmed").count()
    checked_in_bookings = Booking.objects.filter(status="checked_in").count()
    
    # Donations (if you have a Donation model, otherwise set to 0)
    donations = 0  # Replace with: Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    total_messages = ContactMessage.objects.count()
    
    # Room Statistics
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    occupied_rooms = total_rooms - available_rooms
    
    # --- NEW: Room Type Stats ---
    # Annotate each RoomType with the number of rooms that belong to it
    room_types_data = RoomType.objects.annotate(room_count=Count('room'))
    
    # Gallery Stats
    total_gallery_images = Gallery.objects.count()
    active_gallery_images = Gallery.objects.filter(is_active=True).count()
    
    # Events Stats
    today = datetime.now().date()
    total_events = DailyEvent.objects.count()
    upcoming_events = DailyEvent.objects.filter(event_date__gte=today).count()
    
    # Today's Activity
    today_checkins = Booking.objects.filter(check_in_date=today).count()
    today_checkouts = Booking.objects.filter(check_out_date=today).count()
    
    # Recent bookings (last 5)
    recent_bookings = Booking.objects.select_related("room", "room__room_type").order_by("-created_at")[:5]
    
    # Recent activities for timeline
    recent_activities = []
    
    # Add recent bookings to activities
    for booking in Booking.objects.order_by('-created_at')[:3]:
        if booking.status == 'confirmed':
            recent_activities.append({
                'icon': 'check-circle',
                'color': 'success',
                'title': 'New booking confirmed',
                'description': f'Room {booking.room.room_number} - {booking.room.room_type.name}',
                'time': booking.created_at
            })
        elif booking.status == 'pending':
            recent_activities.append({
                'icon': 'clock-history',
                'color': 'warning',
                'title': 'Pending approval',
                'description': f'Booking #{booking.id} awaiting confirmation',
                'time': booking.created_at
            })
    
    # Add recent messages to activities
    for message in ContactMessage.objects.order_by('-created_at')[:2]:
        recent_activities.append({
            'icon': 'envelope',
            'color': 'primary',
            'title': 'New message received',
            'description': f'Contact form submission from {message.name}',
            'time': message.created_at
        })
    
    # Sort activities by time
    recent_activities = sorted(recent_activities, key=lambda x: x['time'], reverse=True)[:4]
    
    # Calculate time ago for activities
    for activity in recent_activities:
        time_diff = datetime.now() - activity['time'].replace(tzinfo=None)
        if time_diff.days > 0:
            activity['time_ago'] = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
        elif time_diff.seconds // 3600 > 0:
            hours = time_diff.seconds // 3600
            activity['time_ago'] = f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = time_diff.seconds // 60
            activity['time_ago'] = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    context = {
        "user": current_user,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "checked_in_bookings": checked_in_bookings,
        "donations": donations,
        "unread_messages": unread_messages,
        "total_messages": total_messages,
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "occupied_rooms": occupied_rooms,
        "room_types_data": room_types_data,  # <-- NEW CONTEXT VARIABLE
        "total_gallery_images": total_gallery_images,
        "active_gallery_images": active_gallery_images,
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "today_checkins": today_checkins,
        "today_checkouts": today_checkouts,
        "recent_bookings": recent_bookings,
        "recent_activities": recent_activities,
    }
    return render(request, "dashboard.html", context)


@custom_login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def booking_detail_api(request, booking_id):
    try:
        booking = Booking.objects.select_related('room', 'room__room_type').get(id=booking_id)

        if request.method == 'GET':
            data = {
                'id': booking.id,
                'customer_name': booking.customer_name,
                'customer_email': booking.customer_email,
                'customer_phone': booking.customer_phone,
                'customer_id_no': booking.customer_id_no or '',
                'customer_id_proof_photo': booking.customer_id_proof_photo.url if booking.customer_id_proof_photo else None,
                'room_id': booking.room.id,
                'room_number': booking.room.room_number,
                'room_type': booking.room.room_type.name,
                'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
                'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
                'guests': booking.guests,
                'special_requests': booking.special_requests or '',
                'total_amount': str(booking.total_amount),
                'status': booking.status,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            return JsonResponse(data)

        elif request.method == 'PUT':
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))

                if 'status' in data:
                    old_status = booking.status
                    new_status = data['status']
                    booking.status = new_status
                    booking.save()

                    # --- Email to Customer ---
                    if booking.customer_email:
                        subject = f"Booking Status Updated - {booking.room.room_type.name}"
                        message_body = (
                            f"Dear {booking.customer_name},\n\n"
                            f"Your booking for Room {booking.room.room_number} "
                            f"({booking.room.room_type.name}) has been updated.\n\n"
                            f"Previous Status: {old_status}\n"
                            f"New Status: {new_status}\n\n"
                            f"Check-in: {booking.check_in_date.strftime('%Y-%m-%d')}\n"
                            f"Check-out: {booking.check_out_date.strftime('%Y-%m-%d')}\n"
                            f"Total Amount: ₹{booking.total_amount}\n\n"
                            f"Thank you for choosing us!\n\n"
                            f"Warm regards,\nTemple Stay Team"
                        )
                        send_email_notification(booking.customer_email, subject, message_body)

                    # --- Email to Admin (English + Hindi) ---
                    admin_email = "divyeshgandhi2000@gmail.com"
                    admin_subject = f"Booking Status Updated - {booking.customer_name}"
                    admin_message = f"""
Booking status has been updated.

Customer Details:
- Name: {booking.customer_name}
- Email: {booking.customer_email}
- Phone: {booking.customer_phone}
- Aadhaar No: {booking.customer_id_no}
- Room: {booking.room.room_type.name}
- Check-in: {booking.check_in_date}
- Check-out: {booking.check_out_date}
- Old Status: {old_status}
- New Status: {new_status}

-----------------------------------------------
हिंदी में सूचना:
बुकिंग की स्थिति अपडेट कर दी गई है।

ग्राहक विवरण:
- नाम: {booking.customer_name}
- ईमेल: {booking.customer_email}
- फ़ोन: {booking.customer_phone}
- आधार नंबर: {booking.customer_id_no}
- कमरा: {booking.room.room_type.name}
- चेक-इन: {booking.check_in_date}
- चेक-आउट: {booking.check_out_date}
- पुरानी स्थिति: {old_status}
- नई स्थिति: {new_status}

कृपया आगे की कार्रवाई के लिए बुकिंग की समीक्षा करें।
"""
                    send_email_notification(admin_email, admin_subject, admin_message)

                    return JsonResponse({'message': 'Booking status updated successfully'})

            else:
                # --- Handle multipart form update ---
                booking.customer_name = request.POST.get('customer_name', booking.customer_name)
                booking.customer_email = request.POST.get('customer_email', booking.customer_email)
                booking.customer_phone = request.POST.get('customer_phone', booking.customer_phone)
                booking.customer_id_no = request.POST.get('customer_id_no', booking.customer_id_no)
                booking.guests = request.POST.get('guests', booking.guests)
                booking.special_requests = request.POST.get('special_requests', booking.special_requests)
                booking.status = request.POST.get('status', booking.status)

                if 'customer_id_proof_photo' in request.FILES:
                    booking.customer_id_proof_photo = request.FILES['customer_id_proof_photo']

                room_id = request.POST.get('room_id')
                if room_id:
                    booking.room = Room.objects.get(id=room_id)

                check_in = request.POST.get('check_in_date')
                check_out = request.POST.get('check_out_date')
                if check_in:
                    booking.check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                if check_out:
                    booking.check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

                nights = (booking.check_out_date - booking.check_in_date).days
                booking.total_amount = nights * booking.room.room_type.price_per_night

                booking.save()

                # --- Email to Customer ---
                if booking.customer_email:
                    subject = f"Booking Updated - {booking.room.room_type.name}"
                    message_body = (
                        f"Dear {booking.customer_name},\n\n"
                        f"Your booking details have been updated.\n"
                        f"New Status: {booking.status}\n\n"
                        f"Check-in: {booking.check_in_date}\n"
                        f"Check-out: {booking.check_out_date}\n"
                        f"Total Amount: ₹{booking.total_amount}\n\n"
                        f"Thank you for choosing us!\nTemple Stay Team"
                    )
                    send_email_notification(booking.customer_email, subject, message_body)

                # --- Email to Admin (English + Hindi) ---
                admin_email = "divyeshgandhi2000@gmail.com"
                admin_subject = f"Booking Updated - {booking.customer_name}"
                admin_message = f"""
Booking details have been updated.

Customer Details:
- Name: {booking.customer_name}
- Email: {booking.customer_email}
- Phone: {booking.customer_phone}
- Aadhaar No: {booking.customer_id_no}
- Room: {booking.room.room_type.name}
- Check-in: {booking.check_in_date}
- Check-out: {booking.check_out_date}
- Status: {booking.status}

-----------------------------------------------
हिंदी में सूचना:
बुकिंग का विवरण अपडेट कर दिया गया है।

ग्राहक विवरण:
- नाम: {booking.customer_name}
- ईमेल: {booking.customer_email}
- फ़ोन: {booking.customer_phone}
- आधार नंबर: {booking.customer_id_no}
- कमरा: {booking.room.room_type.name}
- चेक-इन: {booking.check_in_date}
- चेक-आउट: {booking.check_out_date}
- स्थिति: {booking.status}

कृपया आगे की कार्रवाई के लिए बुकिंग की समीक्षा करें।
"""
                send_email_notification(admin_email, admin_subject, admin_message)

                return JsonResponse({'message': 'Booking updated successfully'})

        elif request.method == 'DELETE':
            booking.delete()
            return JsonResponse({'message': 'Booking deleted successfully'})

    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
    except Exception as e:
        print(f"Error in booking_detail_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    
@custom_login_required
def bookingByAdmin(request):
    current_user = get_current_user(request)

    # Fetch stats
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status="pending").count()
    donations = 0
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    # Recent bookings
    recent_bookings = Booking.objects.select_related(
        "room",
        "room__room_type"
    ).order_by("-created_at")[:5]

    # Current checked-in guests (not checked out)
    active_bookings = Booking.objects.filter(
        status="checked_in"
    ).select_related(
        "room",
        "room__room_type"
    ).order_by("-check_in_date")

    rooms = Room.objects.filter(
        is_available=True
    ).select_related("room_type")

    context = {
        "user": current_user,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "donations": donations,
        "unread_messages": unread_messages,
        "recent_bookings": recent_bookings,
        "active_bookings": active_bookings,
        "rooms": rooms,
    }

    return render(request, "booking_by_admin.html", context)


# @custom_login_required
# def gallary(request):
#     current_user = get_current_user(request)

#     rooms = Room.objects.filter(is_available=True).select_related("room_type")

#     context = {
#         "user": current_user,
#         "rooms": rooms,
#     }
#     return render(request, "gallary.html", context)  

def donation_page(request):
    return render(request, 'donation.html')

def form_pdf(request):
    """
    Form submit होने पर PDF generate करके download कराएगा
    """
    if request.method == "POST":
        name = request.POST.get("name")
        father = request.POST.get("father")
        mother = request.POST.get("mother")
        gaura = request.POST.get("gaura")

        # PDF के लिए HTML template
        html_string = render_to_string("pdf.html", {
            "name": name,
            "father": father,
            "mother": mother,
            "gaura": gaura
        })

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="form_details.pdf"'

        # WeasyPrint से PDF generate
        weasyprint.HTML(string=html_string).write_pdf(response)
        return response

    return JsonResponse({"error": "Method not allowed"}, status=405)

@custom_login_required
def gallery_api(request, image_id=None):
    # Handle _method override for forms
    method = request.POST.get('_method', request.method).upper()
    
    if method == 'GET' and image_id:
        try:
            gallery = Gallery.objects.get(id=image_id)
            return JsonResponse({
                'id': gallery.id,
                'title': gallery.title,
                'category': gallery.category,
                'description': gallery.description,
                'image': gallery.image.url,
                'is_active': gallery.is_active
            })
        except Gallery.DoesNotExist:
            return JsonResponse({'error': 'Image not found'}, status=404)
    
    elif method == 'POST' and not image_id:
        title = request.POST.get('title')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        
        if not all([title, category, image]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        gallery = Gallery.objects.create(
            title=title,
            category=category,
            description=description,
            image=image,
        )
        return JsonResponse({'message': 'Image uploaded successfully', 'id': gallery.id})
    
    elif (method == 'PUT' or request.POST.get('_method') == 'PUT') and image_id:
        try:
            gallery = Gallery.objects.get(id=image_id)
            
            title = request.POST.get('title')
            category = request.POST.get('category')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')
            
            if not all([title, category]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            gallery.title = title
            gallery.category = category
            gallery.description = description
            if image:
                gallery.image = image
            
            gallery.save()
            return JsonResponse({'message': 'Image updated successfully', 'id': gallery.id})
        except Gallery.DoesNotExist:
            return JsonResponse({'error': 'Image not found'}, status=404)
    
    elif method == 'DELETE' and image_id:
        try:
            gallery = Gallery.objects.get(id=image_id)
            gallery.delete()
            return JsonResponse({'message': 'Image deleted successfully'})
        except Gallery.DoesNotExist:
            return JsonResponse({'error': 'Image not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



@custom_login_required
def gallery_page(request):
    galleries = Gallery.objects.all().order_by('-created_at')
    return render(request, 'gallary.html', {'galleries': galleries})


# @custom_login_required
# def dailyevents(request):
#     return render(request, 'dailyevents.html') 
def compress_image(image_file):
    """Compress uploaded image - NO CHANGES"""
    from PIL import Image
    from io import BytesIO
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import sys
    
    img = Image.open(image_file)
    
    # Convert RGBA to RGB if needed
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if too large
    max_size = (1200, 1200)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Compress
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    return InMemoryUploadedFile(
        output, 'ImageField',
        f"{image_file.name.split('.')[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output), None
    )


@custom_login_required
@csrf_exempt
def daily_event_api(request, event_id=None):
    """API endpoint - UNCHANGED LOGIC, just better logging"""
    
    # LOG REQUEST DETAILS
    logger.info(f"=== API Request Start ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Event ID: {event_id}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"POST data: {request.POST.dict()}")
    logger.info(f"FILES: {list(request.FILES.keys())}")
    
    # Handle method override for PUT/DELETE
    method = request.POST.get('_method', request.method).upper()
    logger.info(f"Resolved method: {method}")
    
    # GET single event
    if method == 'GET' and event_id:
        logger.info(f"Processing GET request for event {event_id}")
        try:
            event = DailyEvent.objects.get(id=event_id)
            response_data = {
                'id': event.id,
                'salutation': event.salutation,
                'name': event.name,
                'image': event.image.url if event.image else '',
                'event_date': event.event_date.strftime('%Y-%m-%d'),
                'event_type': event.event_type,
                'description': event.description or '',
                'show_on_home': event.show_on_home
            }
            logger.info(f"GET Success: Returning event data")
            return JsonResponse(response_data)
        except DailyEvent.DoesNotExist:
            logger.error(f"Event {event_id} not found")
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            logger.error(f"GET Error: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    
    # CREATE new event
    elif method == 'POST' and not event_id:
        logger.info("Processing POST request to create new event")
        try:
            salutation = request.POST.get('salutation', '').strip()
            name = request.POST.get('name', '').strip()
            event_date = request.POST.get('event_date', '').strip()
            event_type = request.POST.get('event_type', '').strip()
            description = request.POST.get('description', '').strip()
            show_on_home = request.POST.get('show_on_home') == 'on'
            image = request.FILES.get('image')
            
            logger.info(f"Parsed data - Salutation: {salutation}, Name: {name}, Type: {event_type}, Date: {event_date}")
            logger.info(f"Image received: {image.name if image else 'None'}")
            logger.info(f"Show on home: {show_on_home}")
            
            # Validation
            if not all([salutation, name, event_date, event_type]):
                logger.warning("Validation failed: Missing required fields")
                return JsonResponse({'error': 'कृपया सभी आवश्यक फ़ील्ड भरें'}, status=400)
            
            if not image:
                logger.warning("Validation failed: No image provided")
                return JsonResponse({'error': 'कृपया फोटो अपलोड करें'}, status=400)
            
            # Compress image if needed
            logger.info("Starting image compression...")
            try:
                compressed_image = compress_image(image)
                logger.info("Image compression successful")
            except Exception as e:
                logger.error(f"Image compression failed: {str(e)}", exc_info=True)
                return JsonResponse({'error': f'Image compression failed: {str(e)}'}, status=400)
            
            # Create event
            logger.info("Creating event in database...")
            event = DailyEvent.objects.create(
                salutation=salutation,
                name=name,
                event_date=event_date,
                event_type=event_type,
                description=description,
                show_on_home=show_on_home,
                image=compressed_image
            )
            
            response_data = {
                'message': 'कार्यक्रम सफलतापूर्वक जोड़ा गया!',
                'id': event.id
            }
            logger.info(f"POST Success: Event {event.id} created")
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"POST Error: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Error creating event: {str(e)}'}, status=500)
    
    # UPDATE existing event
    elif method == 'PUT' and event_id:
        logger.info(f"Processing PUT request to update event {event_id}")
        try:
            event = DailyEvent.objects.get(id=event_id)
            
            # Update fields
            salutation = request.POST.get('salutation', '').strip()
            name = request.POST.get('name', '').strip()
            event_date = request.POST.get('event_date', '').strip()
            event_type = request.POST.get('event_type', '').strip()
            description = request.POST.get('description', '').strip()
            show_on_home = request.POST.get('show_on_home') == 'on'
            
            logger.info(f"Update data - Salutation: {salutation}, Name: {name}, Type: {event_type}, Date: {event_date}")
            
            # Validation
            if not all([salutation, name, event_date, event_type]):
                logger.warning("Validation failed: Missing required fields")
                return JsonResponse({'error': 'कृपया सभी आवश्यक फ़ील्ड भरें'}, status=400)
            
            event.salutation = salutation
            event.name = name
            event.event_date = event_date
            event.event_type = event_type
            event.description = description
            event.show_on_home = show_on_home
            
            # Update image if provided
            image = request.FILES.get('image')
            if image:
                logger.info(f"New image provided: {image.name}")
                try:
                    # Delete old image
                    if event.image:
                        event.image.delete(save=False)
                    compressed_image = compress_image(image)
                    event.image = compressed_image
                    logger.info("Image updated successfully")
                except Exception as e:
                    logger.error(f"Image compression failed: {str(e)}", exc_info=True)
                    return JsonResponse({'error': f'Image compression failed: {str(e)}'}, status=400)
            else:
                logger.info("No new image provided, keeping existing")
            
            event.save()
            
            response_data = {
                'message': 'कार्यक्रम सफलतापूर्वक अपडेट किया गया!',
                'id': event.id
            }
            logger.info(f"PUT Success: Event {event.id} updated")
            return JsonResponse(response_data)
            
        except DailyEvent.DoesNotExist:
            logger.error(f"Event {event_id} not found")
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            logger.error(f"PUT Error: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Error updating event: {str(e)}'}, status=500)
    
    # DELETE event
    elif method == 'DELETE' and event_id:
        logger.info(f"Processing DELETE request for event {event_id}")
        try:
            event = DailyEvent.objects.get(id=event_id)
            
            # Delete image file if exists
            if event.image:
                try:
                    event.image.delete(save=False)
                    logger.info("Image file deleted")
                except Exception as e:
                    logger.warning(f"Failed to delete image: {str(e)}")
            
            event.delete()
            logger.info(f"DELETE Success: Event {event_id} deleted")
            return JsonResponse({'message': 'कार्यक्रम सफलतापूर्वक हटाया गया!'})
            
        except DailyEvent.DoesNotExist:
            logger.error(f"Event {event_id} not found")
            return JsonResponse({'error': 'Event not found'}, status=404)
        except Exception as e:
            logger.error(f"DELETE Error: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Error deleting event: {str(e)}'}, status=500)
    
    logger.warning(f"Invalid request - Method: {method}, Event ID: {event_id}")
    return JsonResponse({'error': 'Invalid request'}, status=400)


@custom_login_required
def daily_event_page(request):
    """Render the daily events management page - NO CHANGES"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Auto-delete expired events
    expired_date = timezone.now().date() - timedelta(days=1)
    DailyEvent.objects.filter(event_date__lt=expired_date).delete()
    
    events = DailyEvent.objects.all()
    total_events = events.count()
    
    context = {
        'events': events,
        'total_events': total_events
    }
    return render(request, 'dailyevents.html', context)


@custom_login_required
def generate_event_card(request, event_id):
    logger.info(f"Generating card for event {event_id}")
    try:
        event = DailyEvent.objects.get(id=event_id)
        return render(request, 'event_card.html', {'event': event})
    except DailyEvent.DoesNotExist:
        logger.error(f"Event {event_id} not found")
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        logger.error(f"Error generating card: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
    
# bookings/utils.py
import smtplib

def send_email_notification(receiver_email, subject, message_body):
    """
    Send an email notification using Gmail SMTP (HTML Card View + UTF-8 safe).
    """
    try:
        sender = "divyeshgandhi2000@gmail.com"
        app_password = "dlkn zmpt auql uvxk"  
        
        # 1. Setup the MIME structure
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver_email

        text_content = message_body
        
        html_body_text = message_body.replace('\n', '<br>')
        
        html_content = f"""\
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="background-color: #f4f7f6; margin: 0; padding: 30px 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            
            <!-- Main Card Container -->
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.08);">
                
                <!-- Header (Theme Orange) -->
                <div style="background-color: #ff6b00; color: #ffffff; padding: 25px 20px; text-align: center;">
                    <h6 style="margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px;">श्री भट्टारक यश कीर्ति दिगम्बर जैन धर्मार्थ ट्रस्ट गुरुकुल ऋषभदेव</h6>
                </div>
                
                <!-- Email Body -->
                <div style="padding: 35px 30px; color: #333333; line-height: 1.6; font-size: 16px;">
                    {html_body_text}
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; color: #777777; font-size: 14px; border-top: 1px solid #eeeeee;">
                    <p style="margin: 0 0 8px 0;">Need help? Contact us at <a href="tel:+918233199334" style="color: #ff6b00; text-decoration: none; font-weight: bold;">+91-8233199334</a></p>
                    <p style="margin: 0;">&copy;श्री भट्टारक यश कीर्ति दिगम्बर जैन धर्मार्थ ट्रस्ट गुरुकुल ऋषभदेव. All Rights Reserved.</p>
                </div>
                
            </div>
            
        </body>
        </html>
        """
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')

        msg.attach(part1)
        msg.attach(part2)

        connection = smtplib.SMTP('smtp.gmail.com', 587)
        connection.ehlo()
        connection.starttls()
        connection.login(sender, app_password)
        connection.sendmail(sender, receiver_email, msg.as_string())  
        connection.quit()
        
        print(f"✅ HTML Email sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

@api_view(['GET'])
@permission_classes([AllowAny])
def booking_status(request):
    phone = request.GET.get('customer_phone', '').strip()
    id_no = request.GET.get('customer_id_no', '').strip()

    if not phone and not id_no:
        return Response({'error': 'Please provide a phone number or ID proof number'}, status=400)

    if phone:
        bookings = Booking.objects.filter(customer_phone__icontains=phone).select_related('room', 'room__room_type').order_by('-created_at')
    else:
        bookings = Booking.objects.filter(customer_id_no__icontains=id_no).select_related('room', 'room__room_type').order_by('-created_at')

    if not bookings.exists():
        return Response({'error': 'No booking found for the provided details'}, status=404)

    result = []
    for b in bookings:
        result.append({
            'id': b.id,
            'customer_name': b.customer_name,
            'customer_phone': b.customer_phone,
            'room_number': b.room.room_number,
            'room_type': b.room.room_type.name,
            'check_in_date': b.check_in_date.strftime('%Y-%m-%d'),
            'check_out_date': b.check_out_date.strftime('%Y-%m-%d'),
            'guests': b.guests,
            'total_amount': str(b.total_amount),
            'status': b.status,
            'special_requests': b.special_requests or '',
        })

    return Response(result)