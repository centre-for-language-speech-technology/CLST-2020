---
layout: page
title: Authentication/Authorization
category: Developer
---
## Authentication

We use Django itself for the authentication of users. Most of the authentication is handled in the accounts module. To summarize, nearly everything important is in views.py with the corresponding html pages:<br>
Signup: create a new account.<br>
Login: log in.<br>
Forgot: page for if you forgot the password.<br>
Logout: log out.<br>
ChangePassword: change the password.

You need to be logged in to use the tool. This is made sure by a combination of a simple check at the welcome page, and using a LoginRequiredMixin at all the pages for a script. The Mixin redirects you to the login page if you're not logged in.

## Authorization

We handle permissions for the profiles through an extension of Django named Django-Guardian. The extension allows for an easy way to create permissions and handle them.<br>
The only permission we currently use is a permission to access a project inside the tool. This is defined in the Meta class of the Project class inside models.py (in the scripts module). A user recieves the permission to access a project upon creation of said project. We make sure other users can't get to the project in two ways:
- The user can't see the project in their 'project overview' screen if they aren't the creator. This is achieved through plain Django in project-overview.html.
- The user gets a 403 (Forbidden) message if they try to access the project without permission. This is achieved by a simple check in a lot of views in views.py.

Keep in mind that superusers can't see projects they haven't created, but CAN access them, as they have all permissions by default.
