from django.shortcuts import render

import openpyxl
import json
import requests

def home_view(request):
    files = request.FILES
    if files:
        sedol = files["SEDOL"]

        wb = openpyxl.load_workbook(sedol)

        worksheet = wb["Sheet1"]
        api_url = 'https://api.openfigi.com/v2/mapping'
        headers = {'Content-Type': 'application/json'}
        reading_header = True
        composites = []
        for row in worksheet.iter_rows():
            if reading_header:
                reading_header = False
                continue
            for cell in row:
                print(str(cell.value))
                data = [{"idType": "ID_SEDOL", "idValue": str(cell.value)}]
                response = requests.post(api_url, headers=headers, data=json.dumps(data))
                response_data = response.json()[0]["data"]
                for figi in response_data:
                    composites.append(figi['compositeFIGI'])
                break
            break

        return render(request, 'openfigi_connect/upload_success.html', context={'composites': composites})

    return render(request, 'openfigi_connect/homepage.html')
