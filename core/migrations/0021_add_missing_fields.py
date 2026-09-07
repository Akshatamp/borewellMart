# Generated migration to add missing fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_add_forum_models'),
    ]

    operations = [
        # Add missing fields to Vendor model
        migrations.AddField(
            model_name='vendor',
            name='services_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='vendor',
            name='bookings_count',
            field=models.PositiveIntegerField(default=0),
        ),
        # Add missing fields to City model
        migrations.AddField(
            model_name='city',
            name='slug',
            field=models.SlugField(max_length=100, unique=True, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='service_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='city',
            name='vendor_count',
            field=models.PositiveIntegerField(default=0),
        ),
        # Add missing fields to Service model
        migrations.AddField(
            model_name='service',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, blank=True, null=True),
        ),
        # Add missing fields to ServiceCategory model
        migrations.AddField(
            model_name='servicecategory',
            name='slug',
            field=models.SlugField(max_length=100, unique=True, blank=True, null=True),
        ),
        # Add missing fields to ServiceSubcategory model
        migrations.AddField(
            model_name='servicesubcategory',
            name='slug',
            field=models.SlugField(max_length=100, unique=True, blank=True, null=True),
        ),
        # Add missing fields to Blog model
        migrations.AddField(
            model_name='blog',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, blank=True, null=True),
        ),
        # Add missing fields to BookingPayment model
        migrations.AddField(
            model_name='bookingpayment',
            name='paid_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        # Add missing fields to VendorPayment model
        migrations.AddField(
            model_name='vendorpayment',
            name='plan_type',
            field=models.CharField(max_length=50, default='free'),
        ),
        migrations.AddField(
            model_name='vendorpayment',
            name='amount',
            field=models.DecimalField(max_digits=10, decimal_places=2, default=0),
        ),
        migrations.AddField(
            model_name='vendorpayment',
            name='valid_from',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vendorpayment',
            name='valid_until',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vendorpayment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        # Add missing field to VendorPlan model
        migrations.AddField(
            model_name='vendorplan',
            name='validity_period',
            field=models.PositiveIntegerField(default=30),
        ),
        # Add missing field to ForumPost model
        migrations.AddField(
            model_name='forumpost',
            name='helpful_count',
            field=models.PositiveIntegerField(default=0),
        ),
        # Add missing field to ForumThread model
        migrations.AddField(
            model_name='forumthread',
            name='like_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
