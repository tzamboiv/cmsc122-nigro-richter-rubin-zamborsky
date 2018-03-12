# Generated by Django 2.0.2 on 2018-03-08 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelprefs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='All',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('streetad', models.TextField(default='none')),
                ('poi', models.TextField(default='none')),
                ('divvy', models.TextField(default='none')),
                ('cta', models.TextField(default='none')),
                ('shuttles', models.TextField(default='none')),
                ('driving', models.TextField(default='none')),
                ('bicycling', models.TextField(default='none')),
                ('walking', models.TextField(default='none')),
                ('downtown', models.TextField(default='netiher')),
                ('southside', models.TextField(default='no')),
            ],
        ),
        migrations.CreateModel(
            name='POI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poi_ad', models.TextField()),
            ],
        ),
    ]
