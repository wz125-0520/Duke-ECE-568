# Generated by Django 3.0.2 on 2020-02-07 19:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestofSharer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('des', models.CharField(max_length=200, verbose_name='Destination')),
                ('start_date_0', models.DateTimeField(help_text='Format: 2019-01-01 12:00', verbose_name='Earliest acceptable start date')),
                ('start_date_1', models.DateTimeField(help_text='Format: 2019-01-01 12:00', verbose_name='Latest acceptable start date')),
                ('sharer_num', models.IntegerField(default=1)),
                ('sharer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestofOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('des', models.CharField(max_length=200, verbose_name='Destination')),
                ('start_time', models.DateTimeField(help_text='Format: 2019-01-01 12:00', verbose_name='Start Time')),
                ('status', models.IntegerField(default=0, verbose_name='Ride Status (open, confirmed, complete)')),
                ('share_valid', models.BooleanField(default=False, verbose_name='Do you want to share the ride with others?')),
                ('max_pas_num', models.IntegerField(default=0, verbose_name=' Maximum Number of Passengers')),
                ('total_num', models.IntegerField(default=0)),
                ('sharer_pas_num', models.IntegerField(default=0)),
                ('request', models.CharField(blank=True, max_length=200)),
                ('vehicle', models.CharField(blank=True, max_length=200, verbose_name='Vehicle Type')),
                ('sharer_name', models.CharField(max_length=200)),
                ('driver_name', models.CharField(max_length=200)),
                ('actual_vehicle', models.CharField(max_length=200)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestofDriver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Vehicle', models.CharField(max_length=100)),
                ('Licenseplatenumber', models.IntegerField(default=0)),
                ('Maximumpassengersnumber', models.IntegerField(default=0)),
                ('isDriver', models.BooleanField(default=False)),
                ('s_request', models.CharField(blank=True, max_length=100, verbose_name='Special Request')),
                ('driver_name', models.CharField(max_length=100)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
