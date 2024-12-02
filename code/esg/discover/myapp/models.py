from django.db import models


class WaterResourceManagement(models.Model):
    market_type = models.CharField(max_length=50, verbose_name="市場別")
    year = models.PositiveIntegerField(verbose_name="年份")
    company_code = models.CharField(
        max_length=20, verbose_name="公司代號", blank=True, null=True)
    company_name = models.CharField(max_length=100, verbose_name="公司名稱")
    water_usage = models.FloatField(
        verbose_name="用水量(公噸)", blank=True, null=True)
    data_scope = models.TextField(verbose_name="資料範圍", blank=True, null=True)
    water_intensity = models.FloatField(
        verbose_name="用水密集度(公噸/單位)", blank=True, null=True)
    water_intensity_unit = models.CharField(
        max_length=100, verbose_name="用水密集度-單位", blank=True, null=True)
    certification = models.CharField(
        max_length=255, verbose_name="取得驗證", blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} ({self.year})"

    class Meta:
        verbose_name = "水資源管理"
        verbose_name_plural = "水資源管理"


class WasteManagement(models.Model):
    market_type = models.CharField(max_length=50, verbose_name="市場別")
    year = models.PositiveIntegerField(verbose_name="年份")
    company_code = models.CharField(
        max_length=20, verbose_name="公司代號", blank=True, null=True)
    company_name = models.CharField(max_length=100, verbose_name="公司名稱")
    hazardous_waste = models.CharField(
        max_length=255, verbose_name="有害廢棄物量(公噸)", blank=True, null=True)
    non_hazardous_waste = models.CharField(
        max_length=255, verbose_name="非有害廢棄物量(公噸)", blank=True, null=True)
    total_weight = models.CharField(
        max_length=255, verbose_name="總重量(有害+非有害)(公噸)", blank=True, null=True)
    data_scope = models.TextField(verbose_name="資料範圍", blank=True, null=True)
    waste_intensity = models.CharField(
        max_length=255, verbose_name="廢棄物密集度(公噸/單位)", blank=True, null=True)
    waste_intensity_unit = models.CharField(
        max_length=100, verbose_name="廢棄物密集度-單位", blank=True, null=True)
    certification = models.CharField(
        max_length=255, verbose_name="取得驗證", blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} ({self.year})"

    class Meta:
        verbose_name = "廢棄物管理"
        verbose_name_plural = "廢棄物管理"


class EnergyManagement(models.Model):
    market_type = models.CharField(max_length=50, verbose_name="市場別")
    year = models.IntegerField(verbose_name="年份")
    company_code = models.CharField(max_length=20, verbose_name="公司代號")
    company_name = models.CharField(max_length=100, verbose_name="公司名稱")
    usage_rate = models.CharField(
        max_length=255, verbose_name="使用率(再生能源/總能源)", null=True, blank=True)
    data_scope = models.TextField(verbose_name="資料範圍", null=True, blank=True)
    certification = models.CharField(
        max_length=100, verbose_name="取得驗證", null=True, blank=True)

    def __str__(self):
        return f"{self.company_name} ({self.year})"

    class Meta:
        verbose_name = "能源管理"
        verbose_name_plural = "能源管理"
        unique_together = ("market_type", "year", "company_code")


class GreenhouseGasEmission(models.Model):
    market_type = models.CharField(max_length=10, verbose_name="市場別")
    year = models.PositiveIntegerField(verbose_name="年份")
    company_code = models.CharField(max_length=10, verbose_name="公司代號")
    company_name = models.CharField(max_length=100, verbose_name="公司名稱")

    scope_1_emissions = models.FloatField(
        verbose_name="範疇一-排放量(噸CO2e)", blank=True, null=True)
    scope_1_boundary = models.TextField(
        verbose_name="範疇一-資料邊界", blank=True, null=True)
    scope_1_verification = models.CharField(
        max_length=50, verbose_name="範疇一-取得驗證", blank=True, null=True)

    scope_2_emissions = models.FloatField(
        verbose_name="範疇二-排放量(噸CO2e)", blank=True, null=True)
    scope_2_boundary = models.TextField(
        verbose_name="範疇二-資料邊界", blank=True, null=True)
    scope_2_verification = models.CharField(
        max_length=50, verbose_name="範疇二-取得驗證", blank=True, null=True)

    scope_3_emissions = models.CharField(
        max_length=50, verbose_name="範疇三-排放量(噸CO2e)", blank=True, null=True)
    scope_3_boundary = models.TextField(
        verbose_name="範疇三-資料邊界", blank=True, null=True)
    scope_3_verification = models.CharField(
        max_length=50, verbose_name="範疇三-取得驗證", blank=True, null=True)

    emission_intensity = models.FloatField(
        verbose_name="溫室氣體排放密集度-密集度(噸CO2e/單位)", blank=True, null=True)
    intensity_unit = models.CharField(
        max_length=50, verbose_name="溫室氣體排放密集度-單位", blank=True, null=True)

    class Meta:
        verbose_name = "溫室氣體排放"
        verbose_name_plural = "溫室氣體排放"
        constraints = [
            models.UniqueConstraint(
                fields=['market_type', 'year', 'company_code'], name='unique_market_year_company')
        ]

    def __str__(self):
        return f"{self.company_name} ({self.year})"
