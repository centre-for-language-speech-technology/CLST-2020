# CLST: GiPHouse project
### 

Getting started
---------------

0. Get at least Python 3.7 and install poetry and the requirements as per below.
1. Clone this repository
2. Make sure `poetry` uses your python 3 installation: `poetry env use python3`
3. Run `poetry install`
4. Run `poetry shell`
5. `cd equestria`
6. `./manage.py migrate` to initialise the database
7. `./manage.py createsuperuser` to create the first user
8. `./manage.py runserver` to run a testing server
