from django.shortcuts import render

import openpyxl

def home_view(request):
    files = request.FILES
    if files:
        sedol = files["SEDOL"]

        wb = openpyxl.load_workbook(sedol)

        worksheet = wb["Sheet1"]
        ids = []
        for row in worksheet.iter_rows():
            for cell in row:
                ids.append(str(cell.value))
        return render(request, 'openfigi_connect/upload_success.html')

    return render(request, 'openfigi_connect/homepage.html')
