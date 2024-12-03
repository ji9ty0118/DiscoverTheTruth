from .models import CompanyBoard
from .models import ClimateRiskAndOpportunity
import time
from .forms import ExcelUploadForm
from .models import SustainabilityReport
import string
import random
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import GreenhouseGasEmission
from .models import EnergyManagement
from .models import WasteManagement
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import WaterResourceManagement, EnergyManagement, GreenhouseGasEmission, WasteManagement
from django.db.models import Q
from django.shortcuts import render
from django.forms.models import model_to_dict
from myapp.models import GreenhouseGasEmission  # 替換為實際的 app 名稱
from myapp.models import EnergyManagement  # 替換為實際的 app 名稱
from myapp.models import WasteManagement
from .models import WaterResourceManagement
from django.db import transaction
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def chart(request):
    return render(request, 'chart.html')


def ESGEachCompany(request):
    # 接收篩選條件
    market_type = request.GET.get('market_type', '')
    year = request.GET.get('year', '')
    company_name = request.GET.get('company_name', '')
    company_code = request.GET.get('company_code', '')
    category = request.GET.get('category', '')

    # 根據類別篩選模型
    models = {
        'water': WaterResourceManagement,
        'waste': WasteManagement,
        'energy': EnergyManagement,
        'emission': GreenhouseGasEmission
    }
    selected_model = models.get(category, None)

    data = None
    fields = []
    if selected_model:
        # 篩選數據
        filters = {}
        if market_type:
            filters['market_type'] = market_type
        if year:
            filters['year'] = year
        if company_name:
            filters['company_name__icontains'] = company_name
        if company_code:
            filters['company_code'] = company_code

        data = selected_model.objects.filter(**filters)
        # 提取字段名稱和顯示名稱
        fields = [(field.name, field.verbose_name)
                  for field in selected_model._meta.fields]

    return render(request, 'ESGEachCompany.html', {
        'data': data,
        'fields': fields,
        'category': category,
        'market_type': market_type,
        'year': year,
        'company_name': company_name,
        'company_code': company_code
    })


def ESGReal(request):
    return render(request, 'ESGReal.html')


def ESGRisk(request):
    return render(request, 'ESGRisk.html')


def forget(request):
    return render(request, 'forget.html')


def contact(request):
    return render(request, 'contact.html')


# 生成隨機驗證碼

def generate_captcha():
    characters = string.ascii_uppercase + string.digits  # 可使用字母和數字
    captcha = ''.join(random.choices(characters, k=6))  # 生成6位隨機字符
    return captcha


def login(request):
    if request.method == "POST":
        # 獲取表單輸入
        username = request.POST.get('username')
        password = request.POST.get('password')
        captcha_input = request.POST.get('captcha_input')  # 用戶輸入的驗證碼

        # 獲取 session 中的正確驗證碼
        captcha = request.session.get('captcha', '')

        # 驗證用戶輸入的驗證碼
        if captcha_input != captcha:
            messages.error(request, "驗證碼錯誤，請重新輸入。")
            return redirect('login')  # 驗證碼錯誤，重新載入頁面

        # 驗證用戶名和密碼
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # 登入成功，跳轉到首頁或其他頁面
        else:
            messages.error(request, "使用者名稱或密碼錯誤，請重新輸入。")

    # 生成並儲存新的驗證碼到 session
    captcha = generate_captcha()
    request.session['captcha'] = captcha

    return render(request, 'login.html', {'captcha': captcha, 'message': messages.get_messages(request)})


@csrf_exempt  # 暫時禁用 CSRF 驗證，用於測試 AJAX，正式部署時應移除
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('passwd')
        confirm_password = request.POST.get('passwd1')

        # 密碼不一致檢查
        if password != confirm_password:
            return JsonResponse({'message': '密碼不一致！'})

        # 使用者名稱是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': '使用者名稱已存在！'})

        # Email 是否已被使用
        if User.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email 已被使用！'})

        # 建立新使用者
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)  # 加密密碼
        )

        return JsonResponse({'message': '註冊成功！'})

    return render(request, 'register.html')


def report(request):
    return render(request, 'report.html')


def upload_water_resource_management_data(request):
    file_path = "/Users/lijialing/Desktop/DiscoverTheTruth/2021-2023_ESG/water_resource_management.xlsx"  # 請替換為實際檔案路徑

    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)

        # 檢查必要欄位是否存在
        required_columns = [
            "市場別", "年份", "公司代號", "公司名稱",
            "用水量(公噸)", "資料範圍", "用水密集度(公噸/單位)",
            "用水密集度-單位", "取得驗證"
        ]
        if not all(column in df.columns for column in required_columns):
            return JsonResponse({"error": "Excel 檔案格式錯誤，缺少必要欄位。"}, status=400)

        # 清理數據：處理 NaN 和非數字值
        def clean_value(value):
            if pd.isna(value):  # 如果是 NaN，返回 None
                return None
            if isinstance(value, str) and value.strip() in ["無", "無統計相關數據", "無，無統計相關數據"]:
                return None  # 對無效數據返回 None
            try:
                return float(value)  # 嘗試轉換為浮點數
            except ValueError:
                return None  # 如果無法轉換為數字，返回 None

        # 清理年份欄位：將無效的年份轉為 None 並移除無效年份行
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
        df = df.dropna(subset=["年份"])  # 移除年份為 NaN 的行
        df["年份"] = df["年份"].astype(int)  # 確保年份是整數

        # 清理公司代號：轉為字串並去掉小數點
        df["公司代號"] = df["公司代號"].apply(
            lambda x: str(int(x)) if pd.notna(x) else None)

        # 清理其他數據欄位
        for column in ["用水量(公噸)", "用水密集度(公噸/單位)"]:
            if column in df.columns:
                df[column] = df[column].apply(clean_value)

        # 去除重複資料：依年份和公司代號去重
        df = df.drop_duplicates(subset=["年份", "公司代號"])

        # 插入資料到資料庫
        for _, row in df.iterrows():
            # 檢查資料是否已存在
            if WaterResourceManagement.objects.filter(year=row["年份"], company_code=row["公司代號"]).exists():
                continue  # 如果資料已存在，跳過此行

            # 創建新記錄
            WaterResourceManagement.objects.create(
                market_type=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"],
                water_usage=row.get("用水量(公噸)", None),
                data_scope=row.get("資料範圍", None),
                water_intensity=row.get("用水密集度(公噸/單位)", None),
                water_intensity_unit=row.get("用水密集度-單位", None),
                certification=row.get("取得驗證", None),
            )

        return JsonResponse({"success": "資料成功導入！"})

    except Exception as e:
        return JsonResponse({"error": f"處理檔案時發生錯誤：{str(e)}"}, status=500)


def upload_waste_management_data(request):
    file_path = "/Users/lijialing/Desktop/DiscoverTheTruth/2021-2023_ESG/waste_management.xlsx"  # 替換為實際檔案路徑

    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)

        # 檢查必要欄位是否存在
        required_columns = [
            "市場別", "年份", "公司代號", "公司名稱",
            "有害廢棄物量(公噸)", "非有害廢棄物量(公噸)",
            "總重量(有害+非有害)(公噸)", "資料範圍",
            "廢棄物密集度(公噸/單位)", "廢棄物密集度-單位", "取得驗證"
        ]
        if not all(column in df.columns for column in required_columns):
            return JsonResponse({"error": "Excel 檔案格式錯誤，缺少必要欄位。"}, status=400)

        # 清理數據：處理 NaN 和非數字值
        def clean_value(value):
            if pd.isna(value):  # 如果是 NaN，返回 None
                return None
            if isinstance(value, str) and value.strip() in ["無", "無統計相關數據", "無，無統計相關數據"]:
                return None
            # 嘗試轉為數字
            return float(value) if isinstance(value, (int, float)) else value

        # 清理年份欄位，將無效的年份轉為 None 並移除無效年份行
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
        df = df.dropna(subset=["年份"])  # 移除年份為 NaN 的行
        df["年份"] = df["年份"].astype(int)  # 確保年份是整數

        # 清理公司代號，轉為字串並去掉小數點
        df["公司代號"] = df["公司代號"].apply(
            lambda x: str(int(x)) if pd.notna(x) else None)

        # 清理其他數據欄位
        for column in ["有害廢棄物量(公噸)", "非有害廢棄物量(公噸)", "總重量(有害+非有害)(公噸)", "廢棄物密集度(公噸/單位)"]:
            if column in df.columns:
                df[column] = df[column].apply(clean_value)

        # 去除原始資料中的重複項
        df = df.drop_duplicates(subset=["年份", "公司代號"])

        # 將資料寫入資料庫
        for _, row in df.iterrows():
            # 檢查資料是否已存在
            if WasteManagement.objects.filter(year=row["年份"], company_code=row["公司代號"]).exists():
                print(f"資料已存在：{row['年份']} - {row['公司代號']}")
                continue  # 如果資料已存在，跳過此行

            # 創建新記錄
            WasteManagement.objects.create(
                market_type=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"],
                hazardous_waste=row.get("有害廢棄物量(公噸)", None),
                non_hazardous_waste=row.get("非有害廢棄物量(公噸)", None),
                total_weight=row.get("總重量(有害+非有害)(公噸)", None),
                data_scope=row.get("資料範圍", None),
                waste_intensity=row.get("廢棄物密集度(公噸/單位)", None),
                waste_intensity_unit=row.get("廢棄物密集度-單位", None),
                certification=row.get("取得驗證", None),
            )

        return JsonResponse({"success": "資料成功導入！"})

    except Exception as e:
        return JsonResponse({"error": f"處理檔案時發生錯誤：{str(e)}"}, status=500)


def upload_energy_management_data(request):
    file_path = "/Users/lijialing/Desktop/DiscoverTheTruth/2021-2023_ESG/energy_management.xlsx"  # 替換為實際的檔案路徑

    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)

        # 檢查必要欄位是否存在
        required_columns = [
            "市場別", "年份", "公司代號", "公司名稱",
            "使用率(再生能源/總能源)", "資料範圍", "取得驗證"
        ]
        if not all(column in df.columns for column in required_columns):
            return JsonResponse({"error": "Excel 檔案格式錯誤，缺少必要欄位。"}, status=400)

        # 清理數據：處理 NaN 和非數字值
        def clean_value(value):
            if pd.isna(value):  # 如果是 NaN，返回 None
                return None
            if isinstance(value, str) and value.strip() in ["無", "無統計相關數據", "無，無統計相關數據"]:
                return None
            return value.strip() if isinstance(value, str) else value

        # 清理年份欄位，將無效的年份轉為 None 並移除無效年份行
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
        df = df.dropna(subset=["年份"])  # 移除年份為 NaN 的行
        df["年份"] = df["年份"].astype(int)  # 確保年份是整數

        # 清理公司代號，轉為字串並去掉小數點
        df["公司代號"] = df["公司代號"].apply(
            lambda x: str(int(x)) if pd.notna(x) else None)

        # 清理其他數據欄位
        for column in ["使用率(再生能源/總能源)"]:
            if column in df.columns:
                df[column] = df[column].apply(clean_value)

        # 去除原始資料中的重複項
        df = df.drop_duplicates(subset=["年份", "公司代號", "公司名稱", "市場別"])

        # 將資料寫入資料庫
        for _, row in df.iterrows():
            # 檢查資料是否已存在（基於主要欄位）
            if EnergyManagement.objects.filter(
                market=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"]
            ).exists():
                print(f"重複資料跳過：{row['年份']} - {row['公司代號']} - {row['公司名稱']}")
                continue  # 如果資料已存在，跳過此行

            # 創建新記錄
            EnergyManagement.objects.create(
                market=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"],
                usage_rate=row.get("使用率(再生能源/總能源)", None),
                data_scope=row.get("資料範圍", None),
                certification=row.get("取得驗證", None),
            )

        return JsonResponse({"success": "資料成功導入！"})

    except Exception as e:
        return JsonResponse({"error": f"處理檔案時發生錯誤：{str(e)}"}, status=500)


def upload_greenhouse_gas_emission_data(request):
    file_path = "/Users/lijialing/Desktop/DiscoverTheTruth/2021-2023_ESG/greenhouse_gas_emissions.xlsx"  # 替換為實際的檔案路徑

    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)

        # 檢查必要欄位是否存在
        required_columns = [
            "市場別", "年份", "公司代號", "公司名稱",
            "範疇一-排放量(噸CO2e)", "範疇一-資料邊界", "範疇一-取得驗證",
            "範疇二-排放量(噸CO2e)", "範疇二-資料邊界", "範疇二-取得驗證",
            "範疇三-排放量(噸CO2e)", "範疇三-資料邊界", "範疇三-取得驗證",
            "溫室氣體排放密集度-密集度(噸CO2e/單位)", "溫室氣體排放密集度-單位"
        ]
        if not all(column in df.columns for column in required_columns):
            return JsonResponse({"error": "Excel 檔案格式錯誤，缺少必要欄位。"}, status=400)

        # 清理數據：處理 NaN 和非數字值
        def clean_value(value):
            if pd.isna(value):
                return None
            if isinstance(value, str) and value.strip() in ["無", "無統計相關數據", "無，無統計相關數據"]:
                return None
            return value.strip() if isinstance(value, str) else value

        # 清理年份欄位，將無效的年份轉為 None 並移除無效年份行
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
        df = df.dropna(subset=["年份"])
        df["年份"] = df["年份"].astype(int)

        # 清理公司代號，轉為字串並去掉小數點
        df["公司代號"] = df["公司代號"].apply(
            lambda x: str(int(x)) if pd.notna(x) else None)

        # 清理其他數據欄位
        for column in [
            "範疇一-排放量(噸CO2e)", "範疇二-排放量(噸CO2e)", "範疇三-排放量(噸CO2e)",
            "溫室氣體排放密集度-密集度(噸CO2e/單位)"
        ]:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        # 去除重複項
        df = df.drop_duplicates(subset=["市場別", "年份", "公司代號", "公司名稱"])

        # 將資料寫入資料庫
        for _, row in df.iterrows():
            if GreenhouseGasEmission.objects.filter(
                market=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"]
            ).exists():
                print(f"重複資料跳過：{row['年份']} - {row['公司代號']} - {row['公司名稱']}")
                continue

            GreenhouseGasEmission.objects.create(
                market=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"],
                scope_1_emissions=row.get("範疇一-排放量(噸CO2e)", None),
                scope_1_boundary=row.get("範疇一-資料邊界", None),
                scope_1_verification=row.get("範疇一-取得驗證", None),
                scope_2_emissions=row.get("範疇二-排放量(噸CO2e)", None),
                scope_2_boundary=row.get("範疇二-資料邊界", None),
                scope_2_verification=row.get("範疇二-取得驗證", None),
                scope_3_emissions=row.get("範疇三-排放量(噸CO2e)", None),
                scope_3_boundary=row.get("範疇三-資料邊界", None),
                scope_3_verification=row.get("範疇三-取得驗證", None),
                emission_intensity=row.get("溫室氣體排放密集度-密集度(噸CO2e/單位)", None),
                intensity_unit=row.get("溫室氣體排放密集度-單位", None)
            )

        return JsonResponse({"success": "資料成功導入！"})

    except Exception as e:
        return JsonResponse({"error": f"處理檔案時發生錯誤：{str(e)}"}, status=500)


def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # 獲取上傳的 Excel 檔案
            excel_file = request.FILES['file']

            try:
                # 使用 pandas 讀取 Excel 檔案
                df = pd.read_excel(excel_file, engine='openpyxl')

                # 處理布林欄位，將空值或 NaT 轉為 False
                df['修正後報告書'] = df['修正後報告書'].fillna(False).astype(bool)
                df['英文版修正後報告書'] = df['英文版修正後報告書'].fillna(False).astype(bool)

                # 處理日期欄位，將 NaT 轉為 None
                date_columns = [
                    '上傳日期',
                    '修正後報告書上傳日期',
                    '英文版上傳日期',
                    '英文版修正後報告書上傳日期'
                ]
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(
                            df[col], errors='coerce').dt.date

                # 迭代 DataFrame，將資料存入資料庫
                for _, row in df.iterrows():
                    SustainabilityReport.objects.create(
                        market_type=row.get('市場別'),
                        year=row.get('年份'),
                        company_code=row.get('公司代號'),
                        company_name=row.get('公司名稱'),
                        company_abbreviation=row.get('英文簡稱'),
                        declaration_reason=row.get('申報原因'),
                        industry_category=row.get('產業類別'),
                        report_period=row.get('報告書內容涵蓋期間'),
                        guidelines=row.get('編製依循準則'),
                        third_party_verifier=row.get('第三方驗證單位'),
                        upload_date=row.get('上傳日期') or None,
                        revised_report=row.get('修正後報告書', False),
                        revised_report_upload_date=row.get(
                            '修正後報告書上傳日期') or None,
                        english_report_url=row.get('永續報告書英文版網址'),
                        english_report_upload_date=row.get('英文版上傳日期') or None,
                        english_revised_report=row.get('英文版修正後報告書', False),
                        english_revised_report_upload_date=row.get(
                            '英文版修正後報告書上傳日期') or None,
                        contact_info=row.get('報告書聯絡資訊'),
                        remarks=row.get('備註'),
                    )

                # 導向成功頁面或顯示成功訊息
                return redirect('success_page')

            except Exception as e:
                # 若發生錯誤，顯示錯誤訊息
                return render(request, 'upload.html', {'form': form, 'error': str(e)})

    else:
        form = ExcelUploadForm()

    return render(request, 'upload.html', {'form': form})


def upload_weather_management_data(request):
    # 替換為實際的檔案路徑
    file_path = "/Users/lijialing/Desktop/DiscoverTheTruth/2021-2023_ESG(E)/weather_management.xlsx"

    try:
        # 讀取 Excel 檔案
        df = pd.read_excel(file_path)

        # 檢查必要欄位是否存在
        required_columns = [
            "市場別", "年份", "公司代號", "公司名稱",
            "董事會與管理階層對於氣候相關風險與機會之監督及治理-董事會與管理階層對於氣候相關風險與機會之監督及治理",
            "辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)-辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)",
            "極端氣候事件及轉型行動對財務之影響-極端氣候事件及轉型行動對財務之影響",
            "氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度-氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度",
            "若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響。-若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響。",
            "若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標。-若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標。",
            "若使用內部碳定價作為規劃工具，應說明價格制定基礎。-若使用內部碳定價作為規劃工具，應說明價格制定基礎。",
            "若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量。-若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量。"
        ]
        if not all(column in df.columns for column in required_columns):
            return JsonResponse({"error": "Excel 檔案格式錯誤，缺少必要欄位。"}, status=400)

        # 清理數據：處理 NaN 和非數字值
        def clean_value(value):
            if pd.isna(value):
                return None
            if isinstance(value, str) and value.strip() in ["無", "無統計相關數據", "無，無統計相關數據"]:
                return None
            return value.strip() if isinstance(value, str) else value

        # 清理年份欄位，將無效的年份轉為 None 並移除無效年份行
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
        df = df.dropna(subset=["年份"])
        df["年份"] = df["年份"].astype(int)

        # 清理公司代號，轉為字串並去掉小數點
        df["公司代號"] = df["公司代號"].apply(
            lambda x: str(int(x)) if pd.notna(x) else None)

        # 清理其他數據欄位
        for column in [
            "董事會與管理階層對於氣候相關風險與機會之監督及治理-董事會與管理階層對於氣候相關風險與機會之監督及治理",
            "辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)-辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)",
            "極端氣候事件及轉型行動對財務之影響-極端氣候事件及轉型行動對財務之影響",
            "氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度-氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度",
            "若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響。-若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響。",
            "若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標。-若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標。",
            "若使用內部碳定價作為規劃工具，應說明價格制定基礎。-若使用內部碳定價作為規劃工具，應說明價格制定基礎。",
            "若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量。-若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量。"
        ]:
            if column in df.columns:
                df[column] = df[column].apply(clean_value)

        # 去除重複項
        df = df.drop_duplicates(subset=["市場別", "年份", "公司代號", "公司名稱"])

        # 將資料寫入資料庫
        for _, row in df.iterrows():
            if ClimateRiskAndOpportunity.objects.filter(
                market_type=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"]
            ).exists():
                print(f"重複資料跳過：{row['年份']} - {row['公司代號']} - {row['公司名稱']}")
                continue

            ClimateRiskAndOpportunity.objects.create(
                market_type=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"],
                board_and_management_supervision=row.get(
                    "董事會與管理階層對於氣候相關風險與機會之監督及治理-董事會與管理階層對於氣候相關風險與機會之監督及治理", None),
                impact_on_business_strategy_financials=row.get(
                    "辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)-辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)", None),
                impact_of_extreme_weather_and_transformation_on_financials=row.get(
                    "極端氣候事件及轉型行動對財務之影響-極端氣候事件及轉型行動對財務之影響", None),
                climate_risk_identification_and_management_process=row.get(
                    "氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度-氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度", None),
                scenario_analysis_and_assumptions=row.get(
                    "若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響。-若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響。", None),
                transformation_plan_for_climate_risks=row.get(
                    "若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標。-若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標。", None),
                internal_carbon_pricing_basis=row.get(
                    "若使用內部碳定價作為規劃工具，應說明價格制定基礎。-若使用內部碳定價作為規劃工具，應說明價格制定基礎。", None),
                climate_related_goals_and_progress=row.get(
                    "若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量。-若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量。", None)
            )

        return JsonResponse({"success": "資料成功導入！"})

    except Exception as e:
        return JsonResponse({"error": f"處理檔案時發生錯誤：{str(e)}"}, status=500)


def upload_company_board_data(request):
    file_path = "/Users/lijialing/Desktop/DiscoverTheTruth/2021-2023_ESG(G)/board_of_directors.xlsx"
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)

        # Check that required columns exist in the file
        required_columns = [
            "市場別", "年份", "公司代號", "公司名稱",
            "董事席次(含獨立董事)(席)", "獨立董事席次(席)", "女性董事席次及比率-席",
            "女性董事席次及比率-比率", "董事出席董事會出席率", "董事進修時數符合進修要點比率"
        ]
        if not all(column in df.columns for column in required_columns):
            return JsonResponse({"error": "Excel 檔案格式錯誤，缺少必要欄位。"}, status=400)

        # Clean data: Handle NaN and invalid values
        def clean_value(value):
            if pd.isna(value):  # If NaN, return None
                return None
            if isinstance(value, str) and value.strip() in ["無", "無統計相關數據", "無，無統計相關數據"]:
                return None
            return value.strip() if isinstance(value, str) else value

        # Clean the "年份" column, convert invalid years to None, and drop invalid year rows
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
        df = df.dropna(subset=["年份"])  # Remove rows where "年份" is NaN
        df["年份"] = df["年份"].astype(int)  # Ensure the year is an integer

        # Clean the "公司代號" column, convert it to a string, and remove any decimals
        df["公司代號"] = df["公司代號"].apply(
            lambda x: str(int(x)) if pd.notna(x) else None)

        # Clean other numeric data columns
        numeric_columns = [
            "董事席次(含獨立董事)(席)", "獨立董事席次(席)", "女性董事席次及比率-席",
            "女性董事席次及比率-比率", "董事出席董事會出席率", "董事進修時數符合進修要點比率"
        ]
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce")  # Ensure numeric values
                # Fill NaN with 0 (or None if you prefer)
                df[column] = df[column].fillna(0)

        # Drop duplicates based on key fields
        df = df.drop_duplicates(subset=["年份", "公司代號", "公司名稱", "市場別"])

        # Insert data into the database
        for _, row in df.iterrows():
            # Check if data already exists based on key fields
            if CompanyBoard.objects.filter(
                market_type=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"]
            ).exists():
                print(f"重複資料跳過：{row['年份']} - {row['公司代號']} - {row['公司名稱']}")
                continue  # Skip this row if data already exists

            # Create a new record
            CompanyBoard.objects.create(
                market_type=row["市場別"],
                year=row["年份"],
                company_code=row["公司代號"],
                company_name=row["公司名稱"],
                board_seats_total=row.get(
                    "董事席次(含獨立董事)(席)", 0),  # Default to 0 if NaN
                independent_board_seats=row.get("獨立董事席次(席)", 0),
                female_director_seats=row.get("女性董事席次及比率-席", 0),
                female_director_ratio=row.get("女性董事席次及比率-比率", 0),
                board_attendance_rate=row.get("董事出席董事會出席率", 0),
                training_hours_compliance_rate=row.get("董事進修時數符合進修要點比率", 0),
            )

        return JsonResponse({"success": "資料成功導入！"})

    except Exception as e:
        return JsonResponse({"error": f"處理檔案時發生錯誤：{str(e)}"}, status=500)
