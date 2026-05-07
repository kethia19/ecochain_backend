"""
Adds 'high' to Plant.water_conservation choices.

This is a `choices`-only change — the underlying column is still varchar(20),
no schema-level alteration is required at the DB layer beyond what Django
generates. Existing rows with 'moderate' / 'low' / 'ultra_low' remain valid.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plants', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='water_conservation',
            field=models.CharField(
                choices=[
                    ('high', 'High'),
                    ('moderate', 'Moderate'),
                    ('low', 'Low'),
                    ('ultra_low', 'Ultra-low'),
                ],
                default='moderate',
                max_length=20,
            ),
        ),
    ]
