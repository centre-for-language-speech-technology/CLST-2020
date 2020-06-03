---
layout: page
title: About
permalink: /about/
---

Welcome to the CLST-2020 wiki!

Here we describe how certain stuff should be done. 

We have a few pages. Below you find the git pipeline. We have a seperate page for doing pull requests.
See [Pull requests guidelines](https://github.com/GipHouse/CLST-2020/wiki/pull-requests).

Please see https://github.com/GipHouse/CLST-2020/wiki/Continious-integration-explained for reasons your CI failed.

How to write tests [https://github.com/GipHouse/CLST-2020/wiki/Writing-unit-test](https://github.com/GipHouse/CLST-2020/wiki/Writing-unit-test)


## GIT pipeline
We have one master branch. Everything must work on this branch. That is, ./manage.py runserver should not have any issues. Furthermore, the features should be done. 

To start adding a feature do the following:
1) Start pulling master, to make sure you are up to date.
2) Make a new branch, call it featurebranch. **Give it a descriptive name**. Also if needed write a short description in the branch what it exactly should do. 
Possible starts for branch names are
- structure/
- feature/
- design/
- refactor/

3) Code some cool stuff in the branch.

4) When done, make sure to pull the master to be up to date as well. 

5) NEW!! Make sure you have black installed. This is our format tool. Do:
$poetry shell. 
Now make sure you are outside the git repo:<br>
$ cd .. 
<br>
Now you can check if your code is formatted nicely! Our CI will fail your branch if it does not pass it.<br>
$ black --check CLST-2020<br>
If fails, one can fix it automatically with:<br>
$ black CLST-2020<br>
This will reformat the full directory. One cal also specify one file instead.

6) commit your branch.
7) Do a pull request on your branch, stating you wish to have it merged with master.
8) Ask someone to review your pull request. 

CI:
<br>
We have several CI stuff integrated in our workflow. <br>

In the master we really wish to keep our badges in README working. That is, on the readme page you should see passing for all. 



**DO NOT:**
keep everything locally. Its fine to commit to feature branches!
use one branch, other than master, for adding multiple features. 
Create unneeded branches. (Try to keep a minimal number of branches)
Commit to master (only via pull request)
break other peoples stuff, on master. That is, it is fine to modify code, but it should not _intentionally_ break other features. If you know it breaks something, discuss it first.


