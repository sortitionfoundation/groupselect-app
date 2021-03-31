from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QListView


class TAGenerateFieldsGroup(QGroupBox):
    def __init__(self, ctx):
        super(TAGenerateFieldsGroup, self).__init__("Field Settings")
        self.ctx = ctx

        self.__createUi()

    def __createUi(self):
        models = self.ctx.getFieldsModels()
        modes = {'ignore': 'Ignore fields', 'print': 'Print fields', 'cluster': 'Clustering fields', 'diverse': 'Diversify fields'}

        horizontalLayout = QHBoxLayout()
        for mode in modes:
            horizontalLayout.addWidget(self.__createList(modes[mode], models[mode]))
        self.setLayout(horizontalLayout)

    def __createList(self, name, model):
        list = QListView()
        list.setModel(model)
        list.setDragEnabled(True)
        list.setAcceptDrops(True)
        list.setDropIndicatorShown(True)
        #list.setDragDropMode(QAbstractItemView.DragDrop)
        #list.setDefaultDropAction(Qt.MoveAction)
        #list.setMovement(QListView.Snap)

        layout = QVBoxLayout()
        layout.addWidget(list)
        group = QGroupBox(name)
        group.setLayout(layout)

        return group