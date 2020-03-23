# Table-Allocations Manager

The Sortition Foundation Table-Allocations Manager is an open-source software tool to allocate participants of a Citizens' Assembly (or any similar Deliberative Democracy event) to tables or split them up into smaller groups.

##### How to build this software
This software is based on [QT5](https://doc.qt.io/qt-5/whatsnew59.html) and [PyQt5](https://pypi.org/project/PyQt5/), and can be built using [fbs](https://build-system.fman.io/manual/).

To be able to run this software (after downloading and extracting the archive or cloning the repository), you have to execute the following commands (tested on Linux and Mac):

```
python -m venv venv
source venv/bin/activate
pip install -Ur src/requirements.txt
fbs run
```
This will only allow you to run the software once. If you would like to produce this into an installable software package (a Debian package, a Mac Installer, etc), you will have to follow [these instructions](https://build-system.fman.io/manual/).

For Linux it will be:

```
fbs gengpgkey       # this will generate a signing key
fbs buildvm ubuntu  # to create a Docker VM for building; you can use `arch` / `fedora` instead of `ubuntu`
fbs runvm ubuntu    # to run the VM and enter its CLI
# In the Ubuntu virtual machine:
fbs freeze
fbs release
```
For a Mac it will be:

```
fbs release
```

Documentation on how to run and build on Windows will hopefully follow soon.

##### License
This software is licensed under GNU GPL 3.
