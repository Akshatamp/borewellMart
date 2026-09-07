# Generated migration to add state field to Vendor model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_userprofile_state_alter_vendorplan_plan_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='state',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
