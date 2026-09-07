# Generated migration for vendor equipment

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_add_community_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('drilling_machine', 'Drilling Machine'), ('pump', 'Water Pump'), ('pipe', 'Pipes & Fittings'), ('motor', 'Electric Motor'), ('generator', 'Generator'), ('compressor', 'Air Compressor'), ('tools', 'Hand Tools'), ('other', 'Other Equipment')], default='drilling_machine', max_length=50)),
                ('condition', models.CharField(choices=[('new', 'New'), ('excellent', 'Excellent - Like New'), ('good', 'Good - Minor Wear'), ('fair', 'Fair - Moderate Wear'), ('for_parts', 'For Parts Only')], default='good', max_length=20)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_negotiable', models.BooleanField(default=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='vendor_equipment/')),
                ('year_manufactured', models.PositiveIntegerField(blank=True, null=True)),
                ('brand', models.CharField(blank=True, max_length=100)),
                ('location', models.CharField(help_text='Location of the equipment', max_length=200)),
                ('is_available', models.BooleanField(default=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment', to='core.vendor')),
            ],
            options={
                'verbose_name_plural': 'Vendor Equipment',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EquipmentInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_contacted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment_inquiries', to=settings.AUTH_USER_MODEL)),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to='core.vendorequipment')),
            ],
            options={
                'verbose_name_plural': 'Equipment Inquiries',
                'ordering': ['-created_at'],
            },
        ),
    ]
