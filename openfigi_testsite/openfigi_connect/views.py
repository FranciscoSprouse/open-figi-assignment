from django.http import HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render

import openpyxl
import json
import requests

# The main code for this assignment
# Ideally, constant numbers and Strings in the code would be abstracted out to a constants/strings file,
# but I felt that was overkill for the purpose of this assignment.
# I would also implement unit testing for this, but I also felt that was overkill,
# especially given the minimal level of detail that the Bloomberg api provides,
# most unit tests would have to be made by guessing and checking what error codes Bloomberg returns
# for certain inputs, so that the code could handle them accordingly.

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
            # Only gathers SEDOLs that meet the correct format, by being 7 alphanumeric characters
            # Ignores all other SEDOL numbers
            if len(sedol) == 7 and sedol.isalnum():
               sedols.append({"idType": "ID_SEDOL", "idValue": sedol})

    return sedols


# Fetch the composite FIGI numbers from openfigi given a list of SEDOLS
# Returns a dictionary in the format of {SEDOL Number: [list of composite figis]}
def fetch_compositie_FIGI(sedols):
    bloomberg_api_url = 'https://api.openfigi.com/v2/mapping'
    headers = {'Content-Type': 'application/json'}
    composites = {}

    # Only call the api 5 times before we get rate limited
    # Also, only add 10 SEDOLs per request to avoid rate limiting
    for i in range(5):
        response = requests.post(bloomberg_api_url, headers=headers, data=json.dumps(sedols[i*9:(i*9)+9]))
        # On a good response, parse out the composite FIGIs from the response
        if response.status_code == 200:
            response_json = response.json()
            # The response contains a list of dictionaries, each one corresponds to a specific SEDOL number
            for count, json_dict in enumerate(response_json):
                if "data" in json_dict:
                    for figi in json_dict["data"]:
                        sedol = sedols[(i*9)+count]['idValue']
                        if sedol in composites:
                            composites[sedol].append(figi['compositeFIGI'])
                        else:
                            composites[sedol] = [figi['compositeFIGI']]
                # Errors are returned when no composite FIGI could be found
                elif "error" in json_dict:
                    sedol = sedols[(i*9)+count]['idValue']
                    composites[sedol] = ["Error no id found"]
        # Bloomberg API returns 500 for rate limiting (this is bad practice and should return a 429)
        # If for some reason we start getting rate limited, return what we have
        elif response.status_code == 500:
            return composites
        # In the event that something unexpected happens at the Bloomberg API side, end the task gracefully
        else:
            return None
    return composites
