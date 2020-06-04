---
layout: page
title: Deployment
category: Developer
---

# Deployment

## Docker

Make virtual environment -> run poetry export to requirements.txt -> Install requirements -> Run server


docker build . -t "some tag" in CLST-2020
edit the docker-compose.yml.example and setup.sql.example with passwords, file locations, etc.
[...]

1. Make sure [Docker](https://www.docker.com) and `docker-compose` are installed on the system you plan to run `CLST-2020` on.
2. Clone this repository with `git clone https://github.com/GipHouse/CLST-2020.git` and change your directory to `CLST-2020` (`cd CLST-2020`)
3. There are a couple of files we want to change, namely the `docker-compose.yml.example` and the setup.sql.example file. First clone the `docker_compose` file to a normal `.yml` file and then access it with your texteditor (for this example we will use `nano`).
	- `cp docker-compose.yml.example docker-compose.yml`
	- `nano docker-compose.yml`
4. Change the following in the `docker-compose.yml` file:
	- `[django_secret_key]` to a Django secret key, you can generate one on this [website](https://miniwebtool.com/django-secret-key-generator/).
	- `[postgres_password]` to a random password<sup>1</sup>, you can generate one [here](https://passwordsgenerator.net).
	- `[hostname]` to the hostname of your website.
  - `[admin_email]` to the e-mail address of the admin
5. We need to change one more file located in `database_init`. Execute `cp database_init/setup.sql.example database_init/setup.sql` and edit the file with `nano database_init/setup.sql`.
6. Change the following in the `setup.sql` file:
	- `[postgres_password]` to the password set in <sup>1</sup>.
7. Now you are ready to run the server! Run `docker-compose up -d` to run the three container specified in the `docker-compose.yml` file. You can now access your webpage!
8. To add the first user to your webserver (the "superuser"), you should execute the following commands (while the containers are running, so after executing `docker-compose up -d`):
	- `docker exec -it djangfolio_django /bin/bash`
	- `cd website`
	- `./manage.py createsuperuser`
	- Now, enter your desired username and credentials. Execute `exit` when finished.
9. Congratulations! You can access the settings of the website at `[your domain]/admin` after logging in with the account created in step 8.

## Other

To run the Django server using a different deploy method you will need to:
0. Clone the repository (`git clone https://github.com/GipHouse/CLST-2020.git`) and change directory into `CLST-2020` (`cd CLST-2020`).
1. Make a virtual environment
2. Export dependencies from poetry: `poetry export -f requirements.txt > requirements.txt`
3. Install requirements: `pip install requirements.txt `
4. Run server: `./equestria/manage.py runserver 0.0.0.0:yourPort`

And just like that you are done, your server is now running on all interfaces on port `yourPort`.
