# Generated by Django 2.1.4 on 2020-02-06 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bet', '0005_matchupcoming_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchUpcomingPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.CharField(blank=True, max_length=200, null=True, verbose_name='Đội')),
                ('id_player', models.IntegerField(blank=True, null=True, verbose_name='ID Người chơi')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Người chơi')),
                ('match_upcoming', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bet.MatchUpcoming', verbose_name='Trận đấu')),
            ],
            options={
                'db_table': 'd_cs_go_match_upcoming_player',
            },
        ),
    ]
