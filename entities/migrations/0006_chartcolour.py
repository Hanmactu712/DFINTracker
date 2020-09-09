# Generated by Django 3.0.7 on 2020-07-01 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0005_auto_20200701_0954'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartColour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='first created date')),
                ('last_modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified date')),
                ('created_by_user_id', models.IntegerField(null=True, verbose_name='created by user id')),
                ('created_by_user_name', models.CharField(max_length=200, null=True, verbose_name='created by user name')),
                ('last_modified_by_user_id', models.IntegerField(null=True, verbose_name='last modified by user id')),
                ('last_modified_by_user_name', models.CharField(max_length=200, null=True, verbose_name='last modified by user name')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='is deleted')),
                ('name', models.CharField(max_length=50)),
                ('fill', models.CharField(max_length=10)),
                ('stroke', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]