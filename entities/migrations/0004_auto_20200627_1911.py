# Generated by Django 3.0.7 on 2020-06-27 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0003_auto_20200627_1903'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MetaData',
            new_name='MasterData',
        ),
    ]