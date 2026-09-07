from django.core.management.base import BaseCommand
from core.models import Service
import os


class Command(BaseCommand):
    help = 'Assign images to services from the service_subcategories folder'

    def handle(self, *args, **options):
        # Mapping of image filenames to service IDs (based on actual database IDs)
        # Based on the available images in media/services/subcategories/service_subcategories/

        image_mappings = {
            'Irrigation_Solutions_resized_compressed.jpg': 'irrigation_services',
            'Agricultural_Borewells_resized_compressed.jpg': 'agricultural_services',
            'Borewell_Drillin_resized_compressed.jpg': 'borewell_drilling',
            'Borewell_Casing_Services_resized_compressed.jpg': 'borewell_recharge',
            'Farm_Water_Management_resized_compressed.jpg': 'water_management',
            'Borewell_Development_resized_compressed.jpg': 'borewell_repair_&_maintenance',
            'Groundwater__Soil_Services_resized_compressed.jpg': 'water_testing_&_analysis',
            'Pump_Installation__Maintenance_resized_compressed.jpg': 'pumps_&_motors',
            'Precision_Agriculture_resized_compressed.jpg': 'farm_infrastructure',
            'Water_Yield_Testing_resized_compressed.jpg': 'borewell_deepening_&_re-boring',
            'Water_Quality_Testing_resized_compressed.jpg': 'borewell_cleaning',
            'Borewell_Rehabilitation__Repair_resized_compressed.jpg': 'borewell_electrical_services',
            'Solar_Farming_Solutions_resized_compressed.jpg': 'farm_equipment_rental',
            'Solar_Water_Solutions_resized_compressed.jpg': 'submersible_pumps_&_motors',
            'Pipeline__Irrigation_Services_resized_compressed.jpg': 'pipeline_&_plumbing_services',
            'Borewell_Monitoring__Automation_resized_compressed.jpg': 'borewell_equipment_rental',
            'Rainwater_Harvesting_Integration_resized_compressed.jpg': 'emergency_borewell_services',
            'Borewell_Survey__Site_Selection_resized_compressed.jpg': 'annual_maintenance_contract_(amc)',
            'Environmental__Compliance_Services_resized__58iWd8U.jpg': 'agri_input_dealers',
            # Reuse images for remaining services
            'Agricultural_Borewells_resized_compressed.jpg': 'agriculture_marketplace',  # Reuse agricultural image
            'Solar_Farming_Solutions_resized_compressed.jpg': 'second-hand_agriculture_equipment',  # Reuse
            'Borewell_Monitoring__Automation_resized_compressed.jpg': 'borewell_equipment_dealers',  # Reuse equipment rental
            'Precision_Agriculture_resized_compressed.jpg': 'second-hand_borewell_equipment',  # Reuse again
        }

        base_path = 'media/services/subcategories/service_subcategories/'
        # For database storage, remove the 'media/' prefix as Django adds it automatically
        storage_base_path = 'services/subcategories/service_subcategories/'
        updated_count = 0
        not_found_count = 0
        already_has_image = 0

        for image_file, service_id in image_mappings.items():
            image_path = os.path.join(base_path, image_file)

            # Check if file exists
            if not os.path.exists(image_path):
                self.stdout.write(
                    self.style.WARNING(f'Image file not found: {image_file}')
                )
                not_found_count += 1
                continue

            try:
                service = Service.objects.get(id=service_id)

                if service.image:
                    # Update existing images if they have wrong path
                    if 'media/media/' in service.image.url:
                        # Fix double-media path
                        service.image = storage_base_path + image_file
                        service.save(update_fields=['image'])
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'[FIXED] Corrected image path for "{service.name}"')
                        )
                    else:
                        already_has_image += 1
                        self.stdout.write(
                            self.style.WARNING(f'Service "{service.name}" already has correct image, skipping...')
                        )
                    continue

                # Assign the image with correct path (without 'media/' prefix)
                service.image = storage_base_path + image_file
                service.save(update_fields=['image'])
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Assigned image to "{service.name}"')
                )

            except Service.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Service with ID "{service_id}" not found')
                )
                not_found_count += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Images assigned: {updated_count}'))
        if already_has_image:
            self.stdout.write(
                self.style.WARNING(f'Skipped (already has image): {already_has_image}')
            )
        if not_found_count:
            self.stdout.write(
                self.style.ERROR(f'Not found: {not_found_count}')
            )
        self.stdout.write('='*50)
