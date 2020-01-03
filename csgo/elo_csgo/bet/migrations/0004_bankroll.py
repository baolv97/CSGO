# Generated by Django 2.2 on 2019-12-16 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bet', '0003_auto_20191213_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankRoll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.IntegerField(verbose_name='Tổng tiền')),
                ('change', models.IntegerField(blank=True, null=True, verbose_name='Thay đổi')),
                ('time', models.DateTimeField(blank=True, null=True, verbose_name='Thời gian')),
            ],
            options={
                'verbose_name': 'Tổng tiền',
                'verbose_name_plural': 'Tổng tiền',
                'db_table': 'd_cs_go_bank_roll',
            },
        ),
    ]
