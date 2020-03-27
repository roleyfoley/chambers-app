# Generated by Django 2.0.13 on 2019-06-04 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('complete', 'Complete'), ('lodged', 'Lodged'), ('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('error', 'Error')], default='draft', max_length=12),
        ),
    ]
