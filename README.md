# PDF-Invoice-Generator

Getting everyting ready:

* Create venv.
* Run `pip install -r requirements.txt`
* Run `python manage.py makemigrations && python manage.py migrate`
* Run `python manage.py runserver`
* Fire up a browser of your preference and go to localhost:8000

* Remarks
  * Buyer object hardcoded, because a more elegant way to introduce it has been needed, but not found yet
  * Dynamic formsets not working - need to check how to change TOTAL-FORMS value
