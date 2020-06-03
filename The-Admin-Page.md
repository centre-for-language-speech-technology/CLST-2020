---
layout: page
title: Admin page
---

# The Admin Page
## The command center located at url/admin

### How to Access

You can access the admininstrative section of equestria either by going to equestria.ru.nl/admin or clicking the "Site Admin" item in the dropdown menu of the user icon.

![Admin Overview](CLST-2020/wikiImage/AdminOverview.png)

### Overview

Upon reaching the admin site and having logged in You will be greating with an overview of all database models used within the server.
On the right side of the page You will see a log of recent activities of the site admins.
Please ignore user profiles, it has no real use and is an artifact of implementing personalization.

### Models

* Groups: Currently empty, no clue what it does PLEASE EDIT THIS
* Users: List of all users with detailed information
* Tasks: Currently running server background tasks
* Completed Tasks: Tasks that have been finished as well as additional information
* Projects: Projects created by users
* Pipelines: Language pipelines used in projects
* Profiles: CLAM server profiles for G2P and FA
* Input templates: Templates used by profiles
* Scripts: Connection to scripts for CLAM server
* Processes: Scripts that have been run and their status
* Parameters: Used for dynamic form generation
* Choice parametes: Used for dynamically generated choice fields in forms

### Usage

To add instances to a model, press the "+ Add" button. You will be prompted by a form that contains all necessary fields to create a new instance of that model. Fill these in and press "Save" to finalize the creation process.

To look at or alter instances of a model, click either the model name, or the "Change" button of that model. You will be directed to a complete list of all instances of that model.
While You will not be able to search the entries with a regular search bar in all models, it is possible to apply filters based on the properties of the model on the right side of the page.
Click one of the instances to see all their attributes. In this screen you can also change the values of the fields and update the instance. Instances can also be delted in this screen.
