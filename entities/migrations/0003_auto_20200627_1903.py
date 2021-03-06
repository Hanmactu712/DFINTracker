# Generated by Django 3.0.7 on 2020-06-27 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0002_auto_20200626_1738'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='first created date')),
                ('last_modified_date', models.DateTimeField(auto_now=True, verbose_name='last modified date')),
                ('created_by_user_id', models.IntegerField(null=True, verbose_name='created by user id')),
                ('created_by_user_name', models.CharField(max_length=200, null=True, verbose_name='created by user name')),
                ('last_modified_by_user_id', models.IntegerField(null=True, verbose_name='last modified by user id')),
                ('last_modified_by_user_name', models.CharField(max_length=200, null=True, verbose_name='last modified by user name')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='is deleted')),
                ('type', models.CharField(max_length=200)),
                ('key', models.CharField(max_length=200)),
                ('value', models.TextField(max_length=2000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='entity',
            options={'verbose_name': 'Entity', 'verbose_name_plural': 'Entities'},
        ),
        migrations.AlterModelOptions(
            name='industry',
            options={'verbose_name': 'Industry', 'verbose_name_plural': 'Industries'},
        ),
        migrations.AlterField(
            model_name='balancesheet',
            name='total_equity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=18, verbose_name='Total equity'),
        ),
    ]
