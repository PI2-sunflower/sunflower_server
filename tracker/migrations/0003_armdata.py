# Generated by Django 2.1.2 on 2018-11-27 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_armposition_engine_speed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArmData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation', models.CharField(default='a', max_length=1)),
                ('error_angle_1', models.FloatField(default=0.0)),
                ('error_angle_2', models.FloatField(default=0.0)),
                ('error_angle_3', models.FloatField(default=0.0)),
            ],
        ),
    ]
