from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    amenities = models.TextField(help_text="Comma-separated amenities")
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    floor = models.IntegerField()
    
    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    customer_id_no = models.CharField(max_length=20, blank=True, null=True)  # Aadhaar or any ID number
    customer_id_proof_photo = models.ImageField(upload_to='id_proofs/', blank=True, null=True)  # Photo of the ID proof

    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests = models.IntegerField(validators=[MinValueValidator(1)])
    special_requests = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.id} - {self.customer_name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"


class Login(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    role = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.role})"
    
from django.db import models

class Gallery(models.Model):
    CATEGORY_CHOICES = [
        ('temple', 'Main Temple'),
        ('prayers', 'Morning Prayers'),
        ('cultural', 'Cultural Programs'),
        ('accommodation', 'Accommodation'),
        ('dining', 'Dining Hall'),
        ('gardens', 'Temple Gardens'),
        ('festivals', 'Festivals'),
        ('ceremonies', 'Ceremonies'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='gallery_images/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DailyEvent(models.Model):
    EVENT_TYPES = [
        ('birthday', 'Birthday'),
        ('punyatithi', 'Punyatithi'),
        ('other', 'Other'),
    ]
    
    SALUTATIONS = [
        ('shri', 'श्री'),
        ('smt', 'श्रीमती'),
        ('kumar', 'कुमार'),
        ('kumari', 'कुमारी'),
        ('pandit', 'पंडित'),
        ('swami', 'स्वामी'),
        ('mata', 'माता'),
        ('pita', 'पिता'),
    ]
    
    salutation = models.CharField(max_length=20, choices=SALUTATIONS)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='daily_events/')
    event_date = models.DateField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField(blank=True, null=True)
    show_on_home = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.get_salutation_display()} {self.name} - {self.event_type}"
    
    @property
    def is_expired(self):
        return self.event_date < timezone.now().date()
    
    @classmethod
    def delete_expired_events(cls):
        """Delete events that have passed"""
        from datetime import timedelta
        
        expired_date = timezone.now().date() - timedelta(days=1)
        expired_events = cls.objects.filter(event_date__lt=expired_date)
        count = expired_events.count()
        expired_events.delete()
        return count
    
    def save(self, *args, **kwargs):
        # Only prevent saving if it's a NEW expired event (not update)
        if not self.pk and self.is_expired:
            raise ValueError("Cannot create event with past date")
        super().save(*args, **kwargs)