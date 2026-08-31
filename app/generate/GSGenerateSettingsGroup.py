from typing import TYPE_CHECKING

from math import ceil

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QLineEdit, QComboBox,
                               QGroupBox, QScrollArea, QGridLayout, QFormLayout, QListView, QDataWidgetMapper, QProgressDialog, QSlider)
from PySide6 import QtCore, QtGui

from groupselect import allocate_pandas, AllocatorResult, FieldMode, Algorithm

from GSAppFieldMode import map_field_modes, GSAppFieldMode
from GSProject import settings_lookup, GSProject
from generate.GSAdvancedSettingsDialog import GSAdvancedSettingsDialog
from generate.GSManualDialog import GSManualDialog
from generate.GSHermesSlidersPanel import GSHermesSlidersPanel

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class GSGenerateSettingsGroup(QGroupBox):
    _ctx: 'AppContext'

    def __init__(self, ctx: 'AppContext'):
        super(GSGenerateSettingsGroup, self).__init__('Allocation Settings')
        self._ctx = ctx

        self._mapper = QDataWidgetMapper(self)
        self._mapper.setModel(self._ctx.model_manager['alsettings'])

        self._create_ui()

        self._mapper.toFirst()

    def _create_ui(self):
        layout = QHBoxLayout()
        layout.addWidget(self._create_manual_group(), 3)
        layout.addWidget(self._create_settings_group(), 2)
        self.setLayout(layout)

    def _create_manual_group(self):
        self._manuals_list = QListView()
        self._manuals_list.setModel(self._ctx.model_manager['almanuals'])

        self._btn_add_manual = QPushButton('Add')
        self._btn_add_manual.clicked.connect(self._button_clicked)
        self._btn_del_manual = QPushButton('Delete')
        self._btn_del_manual.clicked.connect(self._button_clicked)

        manual_btns_list = QHBoxLayout()
        manual_btns_list.addWidget(self._btn_add_manual)
        manual_btns_list.addWidget(self._btn_del_manual)
        manual_btns_list_widget = QWidget()
        manual_btns_list_widget.setLayout(manual_btns_list)

        manual_layout = QVBoxLayout()
        manual_layout.addWidget(self._manuals_list)
        manual_layout.addWidget(manual_btns_list_widget)
        manual_group = QGroupBox('Manual Allocations')
        manual_group.setLayout(manual_layout)

        return manual_group

    def _create_settings_group(self):
        self._part_per_group_field = QLineEdit()
        self._part_per_group_field.setValidator(QtGui.QIntValidator(1, 1000, self))
        self._part_per_group_field.textChanged.connect(self.update_groups_estimate)
        self._mapper.addMapping(self._part_per_group_field, settings_lookup.index('n_part_per_group'))

        self._algorithm = QComboBox()
        self._algorithm.addItems([a.name for a in Algorithm])
        self._mapper.addMapping(self._algorithm, settings_lookup.index('algorithm'))
        self._algorithm.currentIndexChanged.connect(self._algorithm_changed)

        # self._cluster_val = QLineEdit()
        # self._mapper.addMapping(self._cluster_val, settings_lookup.index('cluster_val'))
        # self._cluster_val.hide()

        self._slider_widget = GSHermesSlidersPanel(self._ctx)
        model = self._ctx.model_manager["fudiversify"]

        def on_model_changed():
            QTimer.singleShot(0, lambda: self._slider_widget.update_fields())

        model.rowsInserted.connect(lambda *args: on_model_changed())
        model.rowsRemoved.connect(lambda *args: on_model_changed())
        model.dataChanged.connect(lambda *args: on_model_changed())

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._slider_widget)
        self._scroll_area.setMinimumHeight(30)
        self._scroll_area.setMinimumWidth(300)
        self._scroll_label = QLabel("Diversity weights")

        # Set visibility status based of sliders panel.
        is_hermes = Algorithm[self._algorithm.currentText()] == Algorithm.HERMES
        self._scroll_area.setVisible(is_hermes)
        self._scroll_label.setVisible(is_hermes)

        self._groups_calculated = QLabel()

        self._allocations_field = QLineEdit()
        self._allocations_field.setValidator(QtGui.QIntValidator(1, 1000, self))
        self._mapper.addMapping(self._allocations_field, settings_lookup.index('n_allocations'))

        self._btn_advanced = QPushButton('Modify')
        self._btn_advanced.clicked.connect(self._button_clicked)

        m = 50
        form_layout = QFormLayout()
        form_layout.setContentsMargins(m, 0, m, 0)
        form_layout.addRow(QLabel('Group size'), self._part_per_group_field)
        form_layout.addRow(QLabel('Algorithm'), self._algorithm)
        form_layout.addRow(self._scroll_label, self._scroll_area)
        form_layout.addRow(QLabel('Number of groups'), self._groups_calculated)
        form_layout.addRow(QLabel('Number of allocations'), self._allocations_field)
        form_layout.addRow(QLabel('Advanced Settings'), self._btn_advanced)
        form_widget = QWidget()
        form_widget.setLayout(form_layout)

        self._btn_run = QPushButton('Generate Groups!')
        self._btn_run.clicked.connect(self._button_clicked)

        settings_layout = QGridLayout()
        settings_layout.addWidget(form_widget, 1, 1, 1, 1)
        settings_layout.addWidget(self._btn_run, 2, 1, 1, 2)
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)

        return settings_widget

    def update_groups_estimate(self, n_part_per_group: None | str = None):
        project: GSProject = self._ctx.project_manager.project
        if project is None:
            self._groups_calculated.setText('')
            return
        pdata = project.pdata
        if pdata is None or pdata.empty:
            self._groups_calculated.setText('(Computed automatically when participants data imported.)')
        else:
            n_part_per_group = (
                project.settings['n_part_per_group']
                if n_part_per_group is None else
                int(n_part_per_group)
            )
            n_groups = ceil(len(pdata) / n_part_per_group)
            self._groups_calculated.setText(str(n_groups))

    def _algorithm_changed(self):
        project: GSProject = self._ctx.project_manager.project
        if project is None:
            return
        else:
            is_hermes = Algorithm[self._algorithm.currentText()] == Algorithm.HERMES
            self._scroll_area.setVisible(is_hermes)
            self._scroll_label.setVisible(is_hermes)

    def _button_clicked(self):
        sender = self.sender()
        if sender == self._btn_add_manual:
            try:
                allocatables = self._ctx.model_manager['almanuals'].get_allocatables()
                groups = self._ctx.model_manager['almanuals'].get_groups()
            except Exception as ex:
                QMessageBox.critical(self._ctx.main_window, 'Error', f"Error: {ex}")
                return
            ok, participant, group = GSManualDialog.get_input(self, allocatables, groups)
            if not ok:
                return
            self._ctx.model_manager['almanuals'].add_manual(participant, group)
        elif sender == self._btn_del_manual:
            model = self._ctx.model_manager['almanuals']
            if not self._manuals_list.selectedIndexes():
                return
            model.remove_manual(self._manuals_list.currentIndex().row())
        elif sender == self._btn_advanced:
            try:
                attempts_default = self._mapper.model().get_setting('n_attempts')
                seed_default = self._mapper.model().get_setting('seed')
                status, attempts, seed = GSAdvancedSettingsDialog.get_input(self, attempts_default, seed_default)
                if not status: return
                self._mapper.model().set_setting('n_attempts', attempts)
                self._mapper.model().set_setting('seed', seed)
            except Exception as ex:
                QMessageBox.critical(self, 'Error', f"Error occurred while processing your entry: {ex}")
        elif sender == self._btn_run:
            project: GSProject = self._ctx.project_manager.project

            progress_bar = QProgressDialog(
                'Generating table allocations...',
                '',
                0,
                project.settings['n_attempts'],
                self._ctx.main_window,
            )
            progress_bar.setWindowTitle('Generating...')
            progress_bar.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            progress_bar.setAutoClose(False)
            progress_bar.setMinimumDuration(0)
            progress_bar.setCancelButton(None)

            progress_bar.setValue(0)
            progress_bar.show()

            try:
                algorithm = Algorithm[project.settings['algorithm']]
                n_part_per_group = (
                    project.settings['n_allocations']
                    * [project.settings['n_part_per_group']]
                )
                fields = {
                    field_id: map_field_modes(field_usage)
                    for field_usage, field_ids in project.fields_usage.items()
                    for field_id in field_ids
                }
                settings = {
                    key: value
                    for key, value in project.settings.items()
                    if key not in ['n_part_per_group', 'n_allocations']
                }

                # Add pareto probabilities if algorithm is HERMES. Drop probabilities for which the field is not set to
                # mode diversify.
                if algorithm == Algorithm.HERMES:
                    settings["pareto_probs"] = {
                        k: v
                        for k, v in settings["pareto_probs"].items()
                        if k in project.fields_usage[GSAppFieldMode.Diversify]
                    }

                allocation_result: AllocatorResult

                _, _, allocation_result = allocate_pandas(
                    participants=project.pdata_mapped,
                    fields=fields,
                    n_part_per_group=n_part_per_group,
                    manuals=project.manuals,
                    progress_func=lambda steps: progress_bar.setValue(steps),
                    settings=settings,
                    return_full=True,
                    algorithm=algorithm,
                )
            except Exception as ex:
                raise ex
                progress_bar.close()
                QMessageBox.critical(self, 'Error', f"An error occurred during allocation: {ex}")
                return
            else:
                people_data = project.pdata_mapped[project.fields_display()]
                diversity_score = allocation_result.ensemble.calc_diversity_score(people_data)
                meeting_score = allocation_result.ensemble.calc_meeting_norm_score()

                # Close progress bar and display message box with results.
                progress_bar.close()
                QMessageBox.information(
                    self,
                    'Success!',
                    'The allocations were computed successfully.\n\n'
                    f"Diversity score: {diversity_score:.1f}\n"
                    f"Meeting score: {meeting_score:.1%}",
                )

                # Save new allocations to results.
                self._ctx.project_manager.project.results.extend(allocation_result.ensemble)
                self._ctx.model_manager.updated_results()

                # Set project status to unsaved.
                self._ctx.set_unsaved()
        else:
            raise Exception('Unknown button pressed.')
