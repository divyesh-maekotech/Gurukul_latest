from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import RoomType, Room

class Command(BaseCommand):
    help = 'Create sample data for the hotel booking system'

    def handle(self, *args, **options):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hotel.com', 'password')
            self.stdout.write('Created admin user: admin/admin123')

        # Create room types
        room_types_data = [
            {
                'name': 'Standard Room',
                'description': 'Comfortable room with basic amenities',
                'price_per_night': 100.00,
                'capacity': 2,
                'amenities': 'WiFi, TV, Air Conditioning, Private Bathroom'
            },
            {
                'name': 'Deluxe Room',
                'description': 'Spacious room with premium amenities',
                'price_per_night': 150.00,
                'capacity': 3,
                'amenities': 'WiFi, TV, Air Conditioning, Mini Bar, Balcony'
            },
            {
                'name': 'Suite',
                'description': 'Luxury suite with separate living area',
                'price_per_night': 250.00,
                'capacity': 4,
                'amenities': 'WiFi, TV, Air Conditioning, Mini Bar, Balcony, Living Room, Kitchenette'
            }
        ]

        for room_data in room_types_data:
            room_type, created = RoomType.objects.get_or_create(
                name=room_data['name'],
                defaults=room_data
            )
            if created:
                self.stdout.write(f'Created room type: {room_type.name}')

        # Create rooms
        room_types = RoomType.objects.all()
        for floor in range(1, 4):  # 3 floors
            for room_num in range(1, 6):  # 5 rooms per floor
                room_number = f"{floor}0{room_num}"
                room_type = room_types[room_num % len(room_types)]
                
                room, created = Room.objects.get_or_create(
                    room_number=room_number,
                    defaults={
                        'room_type': room_type,
                        'floor': floor,
                        'is_available': True
                    }
                )
                if created:
                    self.stdout.write(f'Created room: {room.room_number}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
