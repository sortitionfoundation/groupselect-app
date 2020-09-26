# GroupSelect App by Sortition Foundation

The GroupSelect App by Sortition Foundation is an open-source tool that allows an easy division of a large group of participants of a citizens' assembly, and any other type of deliberative democracy event into smaller groups. Typically these small groups are tables of 6-8 people, but these could be any type of subgroup. The software allows for diversification across any number of fields, as well as "clustering" based on fields, manual group allocations, and easy post-creation editing of the groups.

This software is based on [QT5](https://doc.qt.io/qt-5/whatsnew59.html) and [PyQt5](https://pypi.org/project/PyQt5/), and can be built using [fbs](https://build-system.fman.io/manual/). Dependencies are managed via pipenv.

To be able to run this software (after downloading and extracting the archive or cloning the repository), you have to execute the following commands to run it or create a software package.

### How to Run This Software
You need to install all dependencies via `pipenv`, and then run the app using `fbs`.

```
pipenv install
fbs run
```
### How to Build This Software

##### For Linux
This following will work for Ubuntu. You will have to build a different VM if you want to create an installer for a different distro.

```
fbs buildvm ubuntu  # to create a virtual machine
fbs runvm ubuntu    # to enter the shell of the virtual machine
# and then inside the VM ...
fbs freeze          # will create an exectuable
fbs installer       # will create an installable package
```

##### For Windows or Mac
```
fbs release
```

### License
This software is licensed under GNU GPL 3.
