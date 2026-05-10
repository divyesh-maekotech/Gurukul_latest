from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'room-types', views.RoomTypeViewSet)
router.register(r'rooms', views.RoomViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('booking/', views.booking_page, name='booking'),
    path('login/', views.login_page, name='login_page'),  # Fixed: render login page
    path('login/submit/', views.login_view, name='login_submit'),  # Fixed: handle login form submission
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('gallary/', views.gallery_page, name='gallary'),
    path('daily-events/', views.daily_event_page, name='daily_events'),
    path('api/daily-events/', views.daily_event_api, name='daily_event_create'),
    path('api/daily-events/<int:event_id>', views.daily_event_api, name='daily_event_detail'),
    path('daily-events/<int:event_id>/card/', views.generate_event_card, name='event_card'),
    path('bookingByAdmin/', views.bookingByAdmin, name='bookingByAdmin'),
    path('bookingByAdmin/bookings/<int:booking_id>/', views.booking_detail_api, name='booking_detail_api'),
    # path('bookingByAdmin/bookings/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
   
    path('api/admin/bookings/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('api/admin/booking-management/', views.admin_booking_management, name='admin_booking_management'),
    path('api/admin/booking-management/<int:booking_id>/', views.admin_booking_management, name='admin_booking_management_detail'),
    # API URLs
    path('api/', include(router.urls)),
    path('api/available-rooms/', views.available_rooms, name='available_rooms'),
    path('api/book-room/', views.create_booking, name='create_booking'),
    path('api/contact/', views.contact_message, name='contact_message'),
    path('api/admin/login/', views.admin_login, name='admin_login'),
    path('api/admin/logout/', views.admin_logout, name='admin_logout'),
    path('api/admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('api/admin/bookings/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('api/admin/messages/', views.admin_messages, name='admin_messages'),
    path('api/rooms/', views.RoomsAPIView.as_view(), name='rooms_api'),
    path('api/bookings/', views.BookingsAPIView.as_view(), name='bookings_api'),
    # path('gallery/', views.gallery_page, name='gallery_page'),
    path('api/gallery/', views.gallery_api, name='gallery_api'),
    path('api/gallery/<int:image_id>/', views.gallery_api, name='gallery_api_detail'),
    path('api/booking-status/', views.booking_status, name='booking_status'), 
]