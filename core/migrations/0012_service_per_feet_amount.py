# Generated migration for adding per_feet_amount field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_add_razorpay_order_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='per_feet_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Rate per feet for borewell drilling (₹/feet)',
                max_digits=10,
                null=True
            ),
        ),
    ]
