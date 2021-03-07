# Equestria: A Forced Alignment Pipeline

Welcome to the Equestria repo, a Django application build for chaining forced alignment scripts on [CLAM](https://clam.readthedocs.io/en/latest/) servers. This application was build on the CLAM servers of the [Centre of Language and Speech Technology](https://www.ru.nl/clst/) of the Radboud University in Nijmegen. It currently features a couple of things:

- Project separation and file storage.
- A backend interface for managing different language pipelines.
- A fully automatic CLAM importer for importing CLAM input templates and parameters into a Django based application.
- Automatic execution of Grapheme to Phoneme (G2P) conversion after forced alignment.

More explanation about the features of this project and a detailed explanation of the database structure is stated below.

## Getting started

This project is built using the [Django](https://github.com/django/django) framework. [Poetry](https://python-poetry.org) is used for dependency management.

### Setup

To setup the project, follow the steps below:

0. Get at least [Python](https://www.python.org) 3.9 installed on your system. An Ubuntu or macOS installation is also needed as some of the dependencies ([pycrypto](https://pypi.org/project/pycrypto/)) of this project will not work on Windows.
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

You can create these database entries yourself or load the default ones that are in a fixture under ```equestria/pipelines/fixtures``` by executing ```./manage.py loaddata pipeline```. Note that these default fixtures do NOT include passwords yet (and the default servers require a password before working). You thus need to obtain the password for the CLAM servers and enter them in the administrator interface. Head over to ```localhost:8000/admin``` and find the added scripts under ```Scripts/Scripts```. For each Script listed, you must enter the password in the ```Password``` field and hit ```Save and refresh```. It is very important to use the ```Save and refresh``` option to pull the configuration files from the CLAM server automatically and load them into our system. The ```SAVE``` option will only save the data you have inputted and will not load any profiles or parameters from the CLAM instance.

After running through these steps the server works as intented and you are able to create projects. We only need to do one last thing before you can actually use the application. When you are running through a pipeline and executing a script, a background process is spawned in the database to be executed in the background. The background processes make sure that the CLAM status is requested once every _x_ seconds and that the files are downloaded to the server after a CLAM process is done. To run the background processes, take the following steps:

1. First, spawn another terminal window as we need to run the background processes in another shell.
2. Navigate to the ```equestria``` folder and execute ```poetry shell``` again such that all dependencies are loaded.
3. Execute ```./manage.py process_tasks``` to spawn a process that monitors the database and executes background tasks.

You are now all set up to develop and test this project. For more information about the project, please read the background information below.

## General Django information
Pulled straight from the [Django website](https://www.djangoproject.com):

_"Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of Web development, so you can focus on writing your app without needing to reinvent the wheel."_

Django is thus a web framework built in Python and has a lot of things needed for running a website with database already created. Using Django, you don't have to worry about handling a Database or creating queries, Django has build-in methods to do all those things. Database entries are created like standard Python classes and automatically handled by Django.

### Django applications

Django works by separating different parts of the website in different applications called _apps_. An app can be created by executing the following command in a Django project: ```django-admin startapp [app name]```. There are currently three self-written apps used in Equestria:

- ```accounts```, this application defines the user account pages.
- ```pipelines```, this application provides the model to define pipelines.
- ```processes```, this application provides all necessary utilities to executes processes on a CLAM server.
- ```projects```, this application provides the features to manage projects and up/download files from the server.
- ```scripts```, this application includes the dependencies needed to synchronise the database of CLAM servers with the one of the websercer.

We will briefly explain some more thing about the applications below.

#### Pipelines application

The ```pipelines``` application includes a model ```Pipeline``` that can be used to define Pipeline instances. When projects are created, a user must specify with which pipeline he/she wants to use. A pipeline defines a Forced Alignment and Grapheen to Phoneem script.

#### Processes application

The ```processes``` application defines a ```Process``` model which creates the ability to synchronises CLAM processes and the processes on the Equestria server. The ```processes``` application also provides models for specifying file and parameter settings.

#### Projects application

The ```projects``` application includes a ```Project``` model which is needed for project creation and bookkeeping. It also keeps track of the uploaded files that are available to the projects.

#### Scripts application

The ```scripts``` application includes a model ```Script``` which saves data regarding a CLAM server. This model can also be used to request a ```clamclient``` instance which can be used to interact with s CLAM server. Password validation will automatically be taken care of. 

### Migrations

Django uses migrations to perform database alterations. A migration is the specification of an alteration of a database model (or more). When, for example, adding a new type of parameter to the project, you will need to create a migration to update the database tables regarding this new model. There are two important thing to remember about migrations:

- How to run migrations.
- How to make migrations.

Running migrations is easy, if you setup the project before reading this you have actually already ran migrations once. To run migrations, you can execute ```./manage.py migrate``` and Django will look for the migration files in the ```migrations``` directories in each installed app. These migration files are just plain Python files and define the database alterations made during project development.

When you have altered a model, added or deleted field or added a completely different model yourself (or deleted one), you should make migrations in order for Django to alter the database such that the new model representation is in synch with the database. To make migrations automatically, you can run ```./manage.py makemigrations```. If you have created a new application and you did make migrations for this applications before, you need to run ```./manage.py makemigrations [app name]```. Note that the app must already be installed in the ```settings.py``` file.

Making migrations and migrating the database is necessary because otherwise the running webserver and the database are not in synch with eachother. For example, if you create a new type of parameter for a script and you do not run migrations, then Django will at some point look for a table in the database that includes the new parameter but won't find one because you did not run migrations yet.

#### Committing migrations

When creating a new model class, you are most likely experimenting a lot and creating migrations a couple of times until your database class is perfect for your needs. Please note that you do not want to commit all new migrations you made, but rather delete the ones you created previously (so not all migrations, just the ones you created in this commit) and create one new migration after you are done altering a model. This ensures that your migrations are kept clean and prevents migration errors.


## CLAM

I'm sure you've by now noticed that we have already stated [CLAM](http://proycon.github.io/clam/) a lot of times. CLAM is, as the name suggests, a wrapper around shell scripts. CLAM allows someone to convert a shell script to a RESTful webservice and web interface. CLAM is used for executing all kinds of scripts (such as the Forced Alignment scripts) used for our project.

There are a couple of advantages for using CLAM over implementing a wrapper around shell scripts ourselves:

- We don't have to maintain a way to execute shell scripts and monitor processes.
- CLAM is a RESTful webservice so we can communicate commands via regular HTTP requests.
- CLAM is written in Python and includes an API that we can use in our Django server.

Adding a script to our application is easy as you have to only setup a new CLAM server and put in in the database of this project. Interfacing options are already implemented in this project or existing methods already existed in the CLAM API.

### Inner workings of a CLAM server

There might be a need for you to set up a CLAM server for a script in the future, it might also be that someone else will set up the CLAM server for you but this background information will still be very handy to read as the inner-workings of this project mirrors the inner-workings of CLAM servers at some points.

There are a couple of important things that must be specified when setting up a CLAM server. These things are:

- Profiles and input templates
- Parameters

Another important thing for setting up a CLAM server is the wrapper script. Because we are not interfacing with the wrapper script in this project, we will not discuss this. For more information about setting up a CLAM server we refer to the [CLAM documentation](https://clam.readthedocs.io/en/latest/).

#### Profiles and input template

Profiles and input templates specify the files that a CLAM server expects as input. A CLAM server can have several profiles which can have several input templates. If you want to run a script on a CLAM server, you must first pick a profile and upload at least one file for all required input templates.

A profile is thus a set of input templates and an input template includes at least the following information:

- A template id
- A template format, classifying the format as a CLAM class
- A label
- A mimetype
- An extension
- If the template is optional
- If the template is unique
- If the template accepts an archive

The above information is also stored by our project in a model class named ```InputTemplate```.

It might be that more then one profile is specified for a CLAM server. Running the CLAM server then requires you to pick a profile before running so that CLAM knows which files to use.

#### Parameters

Parameters specify the parameters that a CLAM server can take for the script to run. Parameters are always global, so parameters are not specified per profile. Parameters in CLAM also have a default value, but in our project one has to always provide another (or the same) default value manually. This is because of the way our project functions.

Parameters can be of the following types:

- Boolean
- Static
- String
- Choice
- Text
- Integer
- Float

For each of these types, a parameter model class is also present in our model. Note that a static parameter can not be passed to CLAM as the parameter is static. For more information about why these parameters exists we refer to the [CLAM documentation](https://clam.readthedocs.io/en/latest/).

### Automatic import of CLAM data

For our project to function, we need to know what CLAM profiles, input templates and parameters are used. Therefor, when pressing ```Save and refresh``` on the admin page of a Script, we automatically ask the CLAM server for its data and import it in our database model. Upon resaving, all profiles, input templates and parameters are recreated. Input templates are static and need not to be modified as are profiles. 

#### Setting default values for parameters

You might need to change default values for parameters, this can be done by looking at the ```Parameters``` section in the ```Script``` details. Check which parameters are linked to the script by remembering their ids. Then go to the ```BaseParameters``` page on the administration view. Set ```Preset``` to ```True``` and change the default value in the corresponding typed parameter. The current parameter type can be seen in the ```Type``` field.
