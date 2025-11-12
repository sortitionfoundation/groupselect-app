# GroupSelect App by Sortition Foundation

The GroupSelect App by Sortition Foundation is an open-source tool that allows an easy division of a large group of participants of a citizens' assembly, and any other type of deliberative democracy event into smaller groups. Typically these small groups are tables of 6-8 people, but these could be any type of subgroup. The software allows for diversification across any number of fields, as well as "clustering" based on fields, manual group allocations, and easy post-creation editing of the groups.

## Dependencies

* This software is based on [Qt6](https://doc.qt.io/qt-6/) and [PySide6](https://pypi.org/project/PySide6/) (a Python binding for Qt). PySide6 is dynamically linked and not distributed with this package. Please refer to its license for terms and conditions.
* This app depends on algorithms provided by the [groupselect](github.com/PhilippVerpoort/groupselect-lib) package.
* This app uses the [datahandling](https://github.com/PhilippVerpoort/datahandling) and the [base-app](https://github.com/PhilippVerpoort/base-app) packages for basic functionalities shared with other apps.

Dependencies are managed with [uv](https://docs.astral.sh/uv/).

### License
This software is licensed under GNU GPL 3.
