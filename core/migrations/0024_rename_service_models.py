# Generated migration for renaming service models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_add_vendor_equipment'),
    ]

    operations = [
        # Step 1: Rename Service (bottom level) → SubService first to free up the "Service" name
        migrations.RenameModel(
            old_name='Service',
            new_name='SubService',
        ),

        # Step 2: Update ForeignKey fields in SubService model
        # Change subcategory field to service
        migrations.RenameField(
            model_name='subservice',
            old_name='subcategory',
            new_name='service',
        ),

        # Update related_name for SubService.service
        migrations.AlterField(
            model_name='subservice',
            name='service',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subservices',
                to='core.servicesubcategory'  # Will point to ServiceSubcategory for now
            ),
        ),

        # Step 3: Rename ServiceSubcategory → Service (now that the "Service" name is free)
        migrations.RenameModel(
            old_name='ServiceSubcategory',
            new_name='Service',
        ),

        # Step 4: Update ForeignKey fields in Service model (formerly ServiceSubcategory)
        # Change category field to sector
        migrations.RenameField(
            model_name='service',
            old_name='category',
            new_name='sector',
        ),

        # Update related_name for Service.sector
        migrations.AlterField(
            model_name='service',
            name='sector',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='services',
                to='core.servicecategory'  # Will point to ServiceCategory for now
            ),
        ),

        # Update SubService.service foreign key to point to the renamed Service model
        migrations.AlterField(
            model_name='subservice',
            name='service',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subservices',
                to='core.service'
            ),
        ),

        # Step 5: Rename ServiceCategory → Sector
        migrations.RenameModel(
            old_name='ServiceCategory',
            new_name='Sector',
        ),

        # Update Service.sector foreign key to point to the renamed Sector model
        migrations.AlterField(
            model_name='service',
            name='sector',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='services',
                to='core.sector'
            ),
        ),

        # Step 6: Update VendorService.subservice field (formerly service)
        migrations.RenameField(
            model_name='vendorservice',
            old_name='service',
            new_name='subservice',
        ),

        # Update related_name for VendorService.subservice
        migrations.AlterField(
            model_name='vendorservice',
            name='subservice',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='vendor_services',
                to='core.subservice'
            ),
        ),

        # Step 7: Update Booking.subservice field (formerly service)
        migrations.RenameField(
            model_name='booking',
            old_name='service',
            new_name='subservice',
        ),

        # Update related_name for Booking.subservice
        migrations.AlterField(
            model_name='booking',
            name='subservice',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bookings',
                to='core.subservice'
            ),
        ),

        # Step 8: Update Enquiry.subservice field (formerly service)
        migrations.RenameField(
            model_name='enquiry',
            old_name='service',
            new_name='subservice',
        ),

        # Update related_name for Enquiry.subservice
        migrations.AlterField(
            model_name='enquiry',
            name='subservice',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='enquiries',
                to='core.subservice'
            ),
        ),

        # Step 9: Update ForumCategory.sector field (formerly service_category)
        migrations.RenameField(
            model_name='forumcategory',
            old_name='service_category',
            new_name='sector',
        ),

        # Update ForumThreadService.subservice field (formerly service)
        migrations.RenameField(
            model_name='forumthreadservice',
            old_name='service',
            new_name='subservice',
        ),
    ]
