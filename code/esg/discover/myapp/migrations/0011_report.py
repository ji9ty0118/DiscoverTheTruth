# Generated by Django 4.2.16 on 2024-12-02 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0010_delete_profile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Report",
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
                ("market_type", models.CharField(max_length=255)),
                ("year", models.IntegerField()),
                ("company_code", models.IntegerField()),
                ("company_name", models.CharField(max_length=255)),
                ("english_abbreviation", models.CharField(max_length=255)),
                ("declaration_reason", models.CharField(max_length=255)),
                ("industry_category", models.CharField(max_length=255)),
                ("report_period", models.CharField(max_length=255)),
                ("preparation_guidelines", models.CharField(max_length=255)),
                (
                    "third_party_verification",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("upload_date", models.DateTimeField()),
                ("revised_report", models.DateTimeField(blank=True, null=True)),
                (
                    "revised_report_upload_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "english_report_url",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("english_report_file", models.DateTimeField(blank=True, null=True)),
                (
                    "english_report_upload_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("revised_english_report", models.DateTimeField(blank=True, null=True)),
                (
                    "revised_english_report_upload_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("report_contact_info", models.CharField(max_length=255)),
                ("remarks", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "永續報告書",
                "verbose_name_plural": "永續報告書",
                "unique_together": {("market_type", "year", "company_code")},
            },
        ),
    ]