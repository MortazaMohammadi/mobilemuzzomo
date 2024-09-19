# Generated by Django 5.0.2 on 2024-09-16 04:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("job", "0001_initial"),
        ("user", "0005_alter_emailupdatecode_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="job",
            name="professional",
        ),
        migrations.AddField(
            model_name="job",
            name="is_avialable",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="job",
            name="is_completed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="job",
            name="complete_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="job",
            name="start_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="JobAcception",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "Job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="job.job"
                    ),
                ),
                (
                    "professional",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="user.professional",
                    ),
                ),
            ],
        ),
    ]
