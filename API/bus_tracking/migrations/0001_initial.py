# Generated by Django 5.1.1 on 2024-09-21 18:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_number', models.CharField(max_length=100)),
                ('current_location_latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('current_location_longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('driver_name', models.CharField(max_length=50, null=True)),
                ('driver_contact', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RouteStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_stationary', models.BooleanField(default=False)),
                ('current_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('stationary_start_time', models.DateTimeField(blank=True, null=True)),
                ('average_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('eta', models.IntegerField(blank=True, null=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bus_tracking.route')),
            ],
        ),
        migrations.CreateModel(
            name='RouteSpeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('speed', models.DecimalField(decimal_places=2, max_digits=5)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('route_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bus_tracking.routestatus')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_name', models.CharField(max_length=100)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('stop_order', models.PositiveIntegerField()),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stops', to='bus_tracking.route')),
            ],
            options={
                'ordering': ['stop_order'],
            },
        ),
        migrations.AddField(
            model_name='routestatus',
            name='upcoming_stop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='upcoming_stop', to='bus_tracking.stop'),
        ),
        migrations.CreateModel(
            name='RouteLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('route_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bus_tracking.routestatus')),
            ],
            options={
                'unique_together': {('route_status', 'timestamp')},
            },
        ),
        migrations.CreateModel(
            name='PassedStop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('route_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passed_stops', to='bus_tracking.routestatus')),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bus_tracking.stop')),
            ],
            options={
                'unique_together': {('route_status', 'stop')},
            },
        ),
    ]
