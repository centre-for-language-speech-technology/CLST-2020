---
layout: page
title: Student help page
permalink: /Student-Use-Case
category: User
---
# Welcome to Equestria

## Your online language toolset

### Logging In

Before you can begin using it, you will need to log in. To do this press the "Log in" button on the home page, or the user icon in the top right.

![LogIn Form](/CLST-2020/wikiImage/loginscreen.png)


You will then be prompted with the log in screen.

![LogIn Form](/CLST-2020/wikiImage/LoginFormScreenshot.png)


This form also offers functionality to register with a new account using the "Sign up" button, as well as resetting your password in case you forgot is using the "Forgotten password" button.


Please note the requirements you have to fullfill when creating a new account as listed on the sign up page.

### Starting Your First Project

After logging in you should head over to the "Project Overview" page. This can be done by clicking the "Project overview" button, clicking the "Select Project" header in the navigation bar, or clicking the user icon and selecting the "My Projects" item.
![Project Overview](/CLST-2020/wikiImage/GoToProjectOverview.png)

![Project Creation](/CLST-2020/wikiImage/ProjectCreateForm.PNG)

In the project creation form, enter a project name you have not used before, also make sure to only use alphanumerical character, i. e. [a-z, A-Z, 0-9] (no spaces) and select an according language/pipeline. Upon clicking "Create" you will be redirected to the "Upload files" screen.

### Uploading Files

Here you can upload the files you want to work with within the project.

![File Upload](/CLST-2020/wikiImage/UploadFilesForm.png)

Mucho Importante: For each audio-text-combination you will have to create a separate project!
You will need to upload both a text file and an audio file. Allowed file formats are .txt, .tg, .wav, or a zip archive containing the necessary files.
Both files should have the same filename (except for the extension .txt, .tg, and .wav). Otherwise, while it might let you click "Continue", correct output is not guaranteed.
Once all files have been uploaded, click the "Continue" button to proceed.

### Forced Alignment

![Forced Alignment](/CLST-2020/wikiImage/FAPage.png)

After clicking the "Continue" button on the upload page, the forced alignment will automatically be run. It will show you the progress via console output on the right side and the current status on the left. Once it is done, click the "Continue" button.

### Grapheme to Phoneme

![Grapheme to Phoneme](/CLST-2020/wikiImage/G2PPage.png)

This page works in very much the same way as Forced Alignment. Grapheme to phoneme will run automatically, once it is done, click the "Continue" button.

### Check Dictionary

![Check Dictionary](/CLST-2020/wikiImage/CheckDictPage.png)

Here you can add words to the dictionary that is used during forced alignment and rerun it. The current version of the dictionary will also be displayed here. If you are satisfied with the current version of the dictionary just click on "Continue to FA Overview". Otherwise alter the content in the textfield above and click on "Update dictionary and rerun FA", so that the Forced Alignment can be done with the new version of the dictionary.

### Overview

![Overview](/CLST-2020/wikiImage/Overview.png)

This is the final page of the forced alignemnt pipeline. Here you can repeat any of the previous steps, download the results, and delete the project if you are done.
If the output does not match what you expected, you can go back to the check dictionary section to add words to it and rerun the forced alignment and grapheen to phoneem steps. you can also add more files via the upload fiels page.
