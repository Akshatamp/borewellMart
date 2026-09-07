from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import InMemoryUploadedFile
from core.models import (
    City, Sector, Service, SubService,
    UserProfile, Vendor, VendorGallery, Review, Blog
)
from PIL import Image
import io


def resize_image(image_file, size=(200, 200), quality=85):
    """Resize image to specified size."""
    if not image_file or not image_file.name:
        return None

    try:
        img = Image.open(image_file)

        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize while maintaining aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)

        # Save to memory
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        # Create new InMemoryUploadedFile
        return InMemoryUploadedFile(
            output, 'ImageField',
            f"{image_file.name.split('.')[0]}_resized.jpg",
            'image/jpeg', output.getbuffer().nbytes, None
        )
    except Exception as e:
        print(f"Error resizing image {image_file.name}: {e}")
        return None


class Command(BaseCommand):
    help = 'Resize all existing images in the database to 200x200'

    def handle(self, *args, **options):
        self.stdout.write('Starting image resize to 200x200...')

        total_resized = 0
        total_errors = 0

        # Process each model with images
        models_to_process = [
            ('City', City.objects.all(), 'image'),
            ('Sector', Sector.objects.all(), 'image'),
            ('Service', Service.objects.all(), 'image'),
            ('SubService', SubService.objects.all(), 'image'),
            ('UserProfile', UserProfile.objects.exclude(profile_image=''), 'profile_image'),
            ('Vendor', Vendor.objects.exclude(logo=''), 'logo'),
            ('VendorGallery', VendorGallery.objects.all(), 'image'),
            ('Review', Review.objects.exclude(customer_image=''), 'customer_image'),
            ('Blog', Blog.objects.exclude(image=''), 'image'),
        ]

        for model_name, queryset, image_field in models_to_process:
            self.stdout.write(f'\nProcessing {model_name}...')
            count = 0
            for obj in queryset:
                try:
                    image_file = getattr(obj, image_field)
                    if image_file and hasattr(image_file, 'name'):
                        resized = resize_image(image_file, size=(200, 200))
                        if resized:
                            setattr(obj, image_field, resized)
                            obj.save(update_fields=[image_field])
                            count += 1
                            total_resized += 1
                except Exception as e:
                    self.stderr.write(f'  Error processing {model_name} ID {obj.id}: {e}')
                    total_errors += 1

            self.stdout.write(f'  Resized {count} images in {model_name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Complete! Resized {total_resized} images total.'
        ))
        if total_errors > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  {total_errors} errors encountered'))
