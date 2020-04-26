[![BCH compliance](https://bettercodehub.com/edge/badge/GipHouse/CLST-2020?branch=master&token=49ec5b1fd248e296877a63e1b775cd5c828877fe)](https://bettercodehub.com/)
![Server testing](https://github.com/GipHouse/CLST-2020/workflows/Server%20testing/badge.svg)
![Coding style](https://github.com/GipHouse/CLST-2020/workflows/Coding%20style/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/GipHouse/CLST-2020/branch/master/graph/badge.svg?token=97JZOEZOAS)](https://codecov.io/gh/GipHouse/CLST-2020)

# Equestria: A Forced Alignment Pipeline

[Coverage Report](https://giphouse.github.io/CLST-2020/)

Welcome on the Equestria repo, a Django application build for chaining forced alignment scripts in a [CLAM](https://clam.readthedocs.io/en/latest/) server. This application was build on the CLAM servers of the [Centre of Language and Speech Technology](https://www.ru.nl/clst/) of the Radboud University in Nijmegen. It currently features a couple of things:

- Project separation and file storage.
- A full blown backend interface for managing different language pipelines.
- A fully automatic CLAM importer for importing CLAM input templates and parameters into this Django based application.
- Automatic execution of Grapheen to Phoneem (G2P) conversion if necessary after forced alignment.

More explanation about the features of this project and a detailed explanation of the database structure is stated below.


## Getting started

This project is built using the [Django](https://github.com/django/django) framework. [Poetry](https://python-poetry.org) is used for dependency management.

### Setup

To setup the project, follow the steps below:

0. Get at least [Python](https://www.python.org) 3.7 installed on your system. An Ubuntu or macOS installation is also needed as some of the dependencies ([pycrypto](https://pypi.org/project/pycrypto/)) of this project will not work on Windows.
1. Clone this repository.
2. If ```pip3``` is not installed on your system yet, execute ```apt install python3-pip``` on your system.
3. Also make sure ```python3-dev``` is installed on your system, execute ```apt install python3-dev```.
4. Install Poetry by following the steps on [their website](https://python-poetry.org/docs/#installation). Make sure poetry is added to ```PATH``` before continuing.
5. Make sure `poetry` uses your python 3 installation: `poetry env use python3`.
6. Run `poetry install` to install all dependencies.
7. Run `poetry shell` to start a shell with the dependencies loaded. This command needs to be ran every time you open a new shell and want to run the development server.
8. Run ```cd equestria``` to change directories to the ```equestria``` folder containing the project.
9. Run ```./manage.py migrate``` to initialise the database and run all migrations.
10. Run ```./manage.py createsuperuser``` to create an administrator that is able to access the backend interface later on.
11. Run ```./manage.py runserver``` to start the development server locally.

Now your server is setup and running on ```localhost:8000```. The administrator interface can be accessed by going to ```localhost:8000/admin```.

The project now works and you are able to interact with the website on your local machine. However, creating a project will result in an error as there are no database entries yet. For the website to work, we need to add a couple of things, namely:

- Two scripts, one being a forced alignment script and the other being a G2P script.
- A Pipeline including the two scripts above.

You can create these database entries yourself or load the default ones that are in a fixture under ```equestria/scripts/fixtures``` by executing ```./manage.py loaddata clam```. Note that these default fixtures do NOT include passwords yet (and the default servers require a password before working). You thus need to obtain the password for the CLAM servers (they are most likely the same for every CLAM server of the CLST faculty) and enter them in the administrator interface. Head over to ```localhost:8000/admin``` and find the added scripts under ```Scripts/Scripts```. For each Script listed, you must enter the password in the ```Password``` field and hit ```Save```.

After running through these steps the server works as intented and you are able to create projects. We only need to do one last thing before you can actually use the application. When you are running through a pipeline and executing a script, a background process is spawned in the database to be executed in the background. The background processes make sure that the CLAM status is requested once every _x_ seconds and that the files are downloaded to the server after a CLAM process is done. To run the background processes, take the following steps:

1. First, spawn another terminal window as we need to run the background processes in another shell.
2. Navigate to the ```equestria``` folder and execute ```poetry shell``` again such that all dependencies are loaded.
3. Execute ```./manage.py process_tasks``` to spawn a process that monitors the database and executes background tasks.

You are now all set up to develop and test this project. For more information about the project, please read the background information below.

## General Django information
What is Django?

### Migrations


## Database structure
