# Generated by Django 4.2.16 on 2024-12-03 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0016_employeedevelop"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanyGovernance",
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
                ("market_type", models.CharField(max_length=50, verbose_name="市場別")),
                ("year", models.PositiveIntegerField(verbose_name="年份")),
                (
                    "company_code",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="公司代號"
                    ),
                ),
                ("company_name", models.CharField(max_length=100, verbose_name="公司名稱")),
                (
                    "annual_conference_count",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="公司年度召開法說會次數(次)"
                    ),
                ),
                (
                    "governance_link",
                    models.URLField(
                        blank=True, null=True, verbose_name="利害關係人或公司治理專區連結"
                    ),
                ),
            ],
            options={
                "verbose_name": "公司治理",
                "verbose_name_plural": "公司治理",
            },
        ),
    ]
