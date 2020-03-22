# Table-Allocations Manager

The Sortition Foundation Table-Allocations Manager is an open-source software tool to allocate participants of a Citizens' Assembly (or any similar Deliberative Democracy event) to tables or split them up into smaller groups.

##### How to build this software
This software is based on [QT5](https://doc.qt.io/qt-5/whatsnew59.html) and [PyQt5](https://pypi.org/project/PyQt5/), and can be built using [fbs](https://build-system.fman.io/manual/).

To run this software (after downloading/cloning it), you have to run the following on Linux:

```
python -m venv venv
source venv/bin/activate
fbs run
```
To build it you will have to set up a a Docker VM as is described [here](https://build-system.fman.io/manual/), and then run `fbs freeze` followed by `fbs release`.

Documentation on how to build for Windows and Mac will follow soon.

##### License
This software is licensed under GNU GPL 3.