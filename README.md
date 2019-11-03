# open-figi-assignment

This repository is a django-backend for a self-hosted web page that recieves an .xlsx file containing a list of SEDOL numbers.
The numbers are parsed from the file, and then queried against the openfigi.com webpage to obtain the corresponding composite FIGI numbers. I do not feel that the repository is production ready since I decided to leave in debug=True which allows django errors to return stack traces to the browser. Additionaly, the code could be cleaned up and organized more for a large scale project by creating a constats and strings file, however since all the relevant code was in a single views.py file I opted out of that. I also opted to keep the css simple, a production ready website would likely have more complicated css for better using interactions.

The main assignment code is in openfigi_testsite/openfigi_connect/views.py

The html docs are in openfigi_testsite/openfigi_connect/templates/openfigi_connect/

The css files are in openfigi_testsite/openfigi_connect/static/

