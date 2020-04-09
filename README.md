# CLST: GiPHouse project
### 

[![BCH compliance](https://bettercodehub.com/edge/badge/GipHouse/CLST-2020?branch=master&token=49ec5b1fd248e296877a63e1b775cd5c828877fe)](https://bettercodehub.com/)
![Server testing](https://github.com/GipHouse/CLST-2020/workflows/Server%20testing/badge.svg)
![Coding style](https://github.com/GipHouse/CLST-2020/workflows/Coding%20style/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/GipHouse/CLST-2020/branch/master/graph/badge.svg?token=97JZOEZOAS)](https://codecov.io/gh/GipHouse/CLST-2020)


Getting started
---------------

Starting the Django server

0. Get at least Python 3.7 and install poetry and the requirements as per below.
1. Clone this repository
2. Make sure `poetry` uses your python 3 installation: `poetry env use python3`
3. Run `poetry install`
4. Run `poetry shell`
5. `cd equestria`
6. `./manage.py migrate` to initialise the database
7. `./manage.py loaddata clam` to load the test CLAM server into the database
8. `./manage.py createsuperuser` to create the first user
9. `./manage.py runserver` to run a testing server
10 `./manage.py process_tasks`to run the background tasks (glue between django and CLAM, for update status etc).
Starting the CLAM test server

1. In another shell, execute `cd fa-clam`.
2. Make sure `poetry` uses your python 3 installation: `poetry env use python3`
3. Run `poetry install`
4. Run `poetry shell`
5. `cd FAclam`
6. `./startserver_development`

Adding an application to the Django migrations

Execute `./manage.py makemigrations app1` when adding app1 to database
