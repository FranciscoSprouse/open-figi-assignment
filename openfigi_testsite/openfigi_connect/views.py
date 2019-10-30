from django.http import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render

import openpyxl
import json
import requests


# The Homepage for the website
# Accepts a GET request to display the home page, or a POST request to upload a sedol file
def home_view(request):
    # Check to see if a file was uploaded in the request
    files = request.FILES
    if files:
        sedol_file = files["SEDOL"]

        try:
            wb = openpyxl.load_workbook(sedol_file)
        except:
            return HttpResponseServerError('<h1>Error Parsing File</h1>')

        sedols = parse_excel_for_sedols(wb)
        composite_figis = fetch_compositie_FIGI(sedols)

        # Return a 404 if no composite FIGIs could be found using the given SEDOLs
        if not composite_figis:
            return HttpResponseNotFound('<h1>No Composite FIGIs were found, \
            this could be the result of ratelimiting </h1>')
        return render(request, 'openfigi_connect/upload_success.html', context={'composites': composite_figis})

    return render(request, 'openfigi_connect/homepage.html')


# Parse an excel workbook for all SEDOL numbers
def parse_excel_for_sedols(workbook):
    worksheet = workbook["Sheet1"]
    reading_header = True
    sedols = []

    for row in worksheet.iter_rows():
        if reading_header:
            reading_header = False
            continue

        for cell in row:
            sedol = str(cell.value)
            if len(sedol) == 7 and sedol.isalnum():
               sedols.append({"idType": "ID_SEDOL", "idValue": sedol})

    return sedols


# Fetch the composite FIGI numbers given a list of SEDOLS
def fetch_compositie_FIGI(sedols):
    bloomberg_api_url = 'https://api.openfigi.com/v2/mapping'
    headers = {'Content-Type': 'application/json'}
    composites = []

    # Only call the api 5 times before we get rate limited
    # Also, only add 10 SEDOLs per request to avoid rate limiting
    for i in range(5):
        response = requests.post(bloomberg_api_url, headers=headers, data=json.dumps(sedols[i:i+9]))
        # On a good response, parse out the composite FIGIs from the response
        if response.status_code == 200:
            response_json = response.json()
            # The response contains a list of dictionaries, each one corresponds to a specific SEDOL number
            for json_dict in response_json:
                if "data" in json_dict:
                    for figi in json_dict["data"]:
                        composites.append(figi['compositeFIGI'])
        # Bloomberg API returns 500 for rate limiting (this is bad practice and should return a 429)
        # If for some reason we start getting rate limited, return what we have
        elif response.status_code == 500:
            print('rate limited')
            return composites
        else:
            return None

    return composites
