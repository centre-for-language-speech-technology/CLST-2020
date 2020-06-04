---
layout: page
title: Add processes on clam
category: Teacher
---
To add processes on CLAM, you need to make sure the CLAM server is running.

Go to `CLST-2020/fa-clam/FAclam/` and run `startserver-development.sh` to start the CLAM server.

Then run `./manage.py loaddata clam`. Alternatively, go to `http://localhost:8000/admin` and add a script yourself. Then you should be able to go to the Forced Alignment page and add processes.
