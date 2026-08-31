"""Group box for the allocation settings form and running the allocation."""

from typing import TYPE_CHECKING

from math import ceil

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QGroupBox,
    QScrollArea,
    QGridLayout,
    QFormLayout,
    QDataWidgetMapper,
    QProgressDialog,
    QSlider,
)
from PySide6 import QtCore, QtGui

from groupselect import allocate_pandas, AllocatorResult, FieldMode, Algorithm

from GSAppFieldMode import map_field_modes, GSAppFieldMode
from GSProject import (
    ALGORITHM_SETTINGS,
    settings_lookup,
    settings_template,
    GSProject,
)
from GSSetup import GSSetup
from generate.GSAdvancedSettingsDialog import GSAdvancedSettingsDialog
from generate.GSHermesSlidersPanel import GSHermesSlidersPanel
from generate.GSParetoSlider import GSParetoSlider

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


# Resolution the [0.0, 1.0] progress fraction reported by groupselect is
# scaled to, since QProgressDialog needs an integer range.
PROGRESS_STEPS = 1000


class GSGenerateSettingsGroup(QGroupBox):
    """Group box for configuring and triggering an allocation run."""

    _ctx: "AppContext"

    def __init__(self, ctx: "AppContext"):
        """Initialise the group box and build the settings UI."""
        super(GSGenerateSettingsGroup, self).__init__("Allocation settings")
        self._ctx = ctx

        self._mapper = QDataWidgetMapper(self)
        self._mapper.setModel(self._ctx.model_manager["alsettings"])

        self._create_ui()

        self._mapper.toFirst()

    def _create_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self._create_settings_group())
        self.setLayout(layout)

    def _create_settings_group(self):
        self._part_per_group_field = QLineEdit()
        self._part_per_group_field.setValidator(
            QtGui.QIntValidator(1, 1000, self)
        )
        self._part_per_group_field.setToolTip(
            "Target number of participants per group. The number of groups "
            "is calculated automatically from the number of participants."
        )
        self._part_per_group_field.textChanged.connect(
            self.update_groups_estimate
        )
        self._mapper.addMapping(
            self._part_per_group_field,
            settings_lookup.index("n_part_per_group"),
        )

        self._algorithm = QComboBox()
        self._algorithm.addItems([a.name for a in Algorithm])
        self._algorithm.setToolTip(
            "Algorithm used to compute the allocation. Different "
            "algorithms trade off diversity, meeting variety, and speed "
            "differently, and offer different advanced settings below."
        )
        self._mapper.addMapping(
            self._algorithm, settings_lookup.index("algorithm")
        )

        self._slider_widget = GSHermesSlidersPanel(self._ctx)
        model = self._ctx.model_manager["fudiversify"]

        def on_model_changed(*args):
            QTimer.singleShot(0, lambda: self._slider_widget.update_fields())

        model.rowsInserted.connect(on_model_changed)
        model.rowsRemoved.connect(on_model_changed)
        model.dataChanged.connect(on_model_changed)
        # `updated_project()` (called on project open/new/close) only emits
        # `layoutChanged`, not the row/data signals above -- without this,
        # the panel would keep showing the previous project's sliders until
        # a field was next dragged in/out of the Diversify list.
        model.layoutChanged.connect(on_model_changed)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._slider_widget)
        self._scroll_area.setMinimumHeight(30)
        self._scroll_area.setMinimumWidth(300)
        self._scroll_label = QLabel("Diversity weights")
        hermes_weights_tooltip = (
            "Per-field diversity weight: higher values make the algorithm "
            "prioritise diversifying that field more strongly relative to "
            "the other Diversify fields."
        )
        self._scroll_label.setToolTip(hermes_weights_tooltip)
        self._scroll_area.setToolTip(hermes_weights_tooltip)

        # DREAM's single, scalar counterpart to HERMES's per-field
        # `pareto_probs` sliders above -- same widget, just one of it, and
        # sharing its "Diversity weights" label since only one of the two
        # rows is ever shown at a time (see `_apply_algorithm_state`).
        self._pareto_prob_label = QLabel("Diversity weights")
        dream_weight_tooltip = (
            "Overall diversity weight: higher values make the algorithm "
            "prioritise diversifying across all Diversify fields more "
            "strongly, potentially at the cost of other objectives."
        )
        self._pareto_prob_label.setToolTip(dream_weight_tooltip)
        self._pareto_prob_slider = GSParetoSlider(
            settings_template["pareto_prob"],
            self._pareto_prob_changed,
            tooltip=dream_weight_tooltip,
        )

        # Show/hide whichever of the above isn't used by the currently
        # chosen algorithm. Two separate triggers, deliberately reading the
        # algorithm from two different places:
        #  - picking a new algorithm in the combo box needs to update this
        #    right away, but `QDataWidgetMapper` only writes a mapped
        #    widget's value back into the model on focus-out -- reading
        #    `project.settings["algorithm"]` at this point could still see
        #    the *previous* algorithm, so this one reads the combo box
        #    itself instead, same as it did before it was mapped in here;
        #  - opening a different project updates `project.settings`
        #    directly and reliably, but may leave the combo box showing the
        #    same algorithm name as before (`currentIndexChanged` then
        #    never fires) even though e.g. `pareto_prob` still needs
        #    resyncing -- `alsettings`'s `dataChanged` fires on every
        #    `updated_project()` regardless, so that one reads the project.
        self._algorithm.currentIndexChanged.connect(
            self._algorithm_combo_changed
        )
        self._ctx.model_manager["alsettings"].dataChanged.connect(
            self._project_settings_changed
        )
        self._project_settings_changed()

        self._groups_calculated = QLabel()
        self._groups_calculated.setToolTip(
            "Number of groups, calculated automatically as the number of "
            "participants divided by the group size, rounded up."
        )

        self._allocations_field = QLineEdit()
        self._allocations_field.setValidator(
            QtGui.QIntValidator(1, 1000, self)
        )
        self._allocations_field.setToolTip(
            "Number of independent allocations (rounds) to generate in "
            "this run, e.g. so participants can be reshuffled for a "
            "second session."
        )
        self._mapper.addMapping(
            self._allocations_field, settings_lookup.index("n_allocations")
        )

        self._btn_advanced = QPushButton("Modify")
        self._btn_advanced.setToolTip(
            "Open advanced settings for the chosen algorithm: number of "
            "attempts, random seed, and other algorithm-specific "
            "parameters."
        )
        self._btn_advanced.clicked.connect(self._button_clicked)

        # Lets the user choose whether "Generate" creates a new setup
        # (ensemble) or appends the new allocations to an existing one.
        # Disabled (so it can't even be opened) while no setup exists yet,
        # since "Create new setup" is then the only possible choice anyway.
        self._setup_target = QComboBox()
        self._setup_target.setToolTip(
            "Choose whether to file the newly generated round(s) under a "
            "new setup, or append them to an existing setup in the "
            "Results tab."
        )
        self._refresh_setup_target()
        self._ctx.model_manager["results_tree"].layoutChanged.connect(
            self._refresh_setup_target
        )

        m = 50
        form_layout = QFormLayout()
        form_layout.setContentsMargins(m, 0, m, 0)
        form_layout.addRow(QLabel("Group size"), self._part_per_group_field)
        form_layout.addRow(QLabel("Number of groups"), self._groups_calculated)
        form_layout.addRow(QLabel("Number of rounds"), self._allocations_field)
        form_layout.addRow(QLabel("Target Setup"), self._setup_target)
        form_layout.addRow(QLabel("Algorithm"), self._algorithm)
        form_layout.addRow(self._scroll_label, self._scroll_area)
        form_layout.addRow(self._pareto_prob_label, self._pareto_prob_slider)
        form_layout.addRow(QLabel("Advanced Settings"), self._btn_advanced)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)

        self._btn_run = QPushButton("Generate Groups!")
        self._btn_run.setToolTip(
            "Run the selected algorithm to generate group allocation(s), "
            "using the current field settings and manual assignments."
        )
        self._btn_run.clicked.connect(self._button_clicked)

        settings_layout = QGridLayout()
        settings_layout.addWidget(form_widget, 1, 1, 1, 1)
        settings_layout.addWidget(self._btn_run, 2, 1, 1, 2)
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)

        return settings_widget

    def _refresh_setup_target(self):
        """Repopulate the "target setup" drop-down from the project."""
        project = self._ctx.project_manager.project
        setups = project.setups if project is not None else []

        previous_selection = self._setup_target.currentData()
        self._setup_target.blockSignals(True)
        self._setup_target.clear()
        self._setup_target.addItem("Create new setup", None)
        for i, setup in enumerate(setups):
            self._setup_target.addItem(setup.name, i)
        restore_index = self._setup_target.findData(previous_selection)
        self._setup_target.setCurrentIndex(max(restore_index, 0))
        self._setup_target.setEnabled(bool(setups))
        self._setup_target.blockSignals(False)

    def update_groups_estimate(self, n_part_per_group: None | str = None):
        """Recompute and display the estimated number of groups."""
        project: GSProject = self._ctx.project_manager.project
        if project is None:
            self._groups_calculated.setText("")
            return
        pdata = project.pdata
        if pdata is None or pdata.empty:
            self._groups_calculated.setText(
                "(Computed automatically when participants data imported.)"
            )
        else:
            n_part_per_group = (
                project.settings["n_part_per_group"]
                if n_part_per_group is None
                else int(n_part_per_group)
            )
            n_groups = ceil(len(pdata) / n_part_per_group)
            self._groups_calculated.setText(str(n_groups))

    def _pareto_prob_changed(self, value: float) -> None:
        project = self._ctx.project_manager.project
        if project is not None:
            project.settings["pareto_prob"] = value

    def _algorithm_combo_changed(self, *args):
        """React to the user picking a different algorithm in the combo box."""
        if self._ctx.project_manager.project is not None:
            self._apply_algorithm_state(
                Algorithm[self._algorithm.currentText()]
            )

    def _project_settings_changed(self, *args):
        """React to `alsettings` changing (in particular, a project switch)."""
        project: GSProject = self._ctx.project_manager.project
        if project is not None:
            self._apply_algorithm_state(
                Algorithm[project.settings["algorithm"]]
            )

    def _apply_algorithm_state(self, algorithm: "Algorithm") -> None:
        """Show/hide the diversity-weights row(s) unused by `algorithm`."""
        project: GSProject = self._ctx.project_manager.project
        used = ALGORITHM_SETTINGS[algorithm]
        is_hermes = "pareto_probs" in used
        is_dream = "pareto_prob" in used
        self._scroll_area.setVisible(is_hermes)
        self._scroll_label.setVisible(is_hermes)
        self._pareto_prob_label.setVisible(is_dream)
        self._pareto_prob_slider.setVisible(is_dream)
        self._pareto_prob_slider.set_value(project.settings["pareto_prob"])

    def _button_clicked(self):
        sender = self.sender()
        if sender == self._btn_advanced:
            try:
                # QDataWidgetMapper only writes a mapped widget's edited
                # value back into the model on focus-out; force that now so
                # a just-picked algorithm (or edited group size/allocation
                # count) is reflected below even without an intervening
                # focus change.
                self._mapper.submit()
                project: GSProject = self._ctx.project_manager.project
                algorithm = Algorithm[project.settings["algorithm"]]
                attempts_default = self._mapper.model().get_setting(
                    "n_attempts"
                )
                seed_default = self._mapper.model().get_setting("seed")
                swap_rounds_default = self._mapper.model().get_setting(
                    "swap_rounds"
                )
                cluster_tables_default = self._mapper.model().get_setting(
                    "cluster_tables"
                )
                (
                    status,
                    attempts,
                    seed,
                    swap_rounds,
                    cluster_tables,
                ) = GSAdvancedSettingsDialog.get_input(
                    self,
                    algorithm,
                    attempts_default,
                    seed_default,
                    swap_rounds_default,
                    cluster_tables_default,
                )
                if not status:
                    return
                self._mapper.model().set_setting("n_attempts", attempts)
                self._mapper.model().set_setting("seed", seed)
                self._mapper.model().set_setting("swap_rounds", swap_rounds)
                self._mapper.model().set_setting(
                    "cluster_tables", cluster_tables
                )
            except Exception as ex:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error occurred while processing your entry: {ex}",
                )
        elif sender == self._btn_run:
            # See the comment in the "_btn_advanced" branch above -- forces
            # any just-edited group size/allocation count/algorithm to be
            # reflected in `project.settings` before it's read below.
            self._mapper.submit()
            project: GSProject = self._ctx.project_manager.project
            algorithm = Algorithm[project.settings["algorithm"]]

            # groupselect's progress_func reports a float fraction complete
            # in [0.0, 1.0], the same for every algorithm; QProgressDialog
            # needs an integer range, so scale that fraction up to
            # PROGRESS_STEPS steps of resolution.
            progress_bar = QProgressDialog(
                "Generating table rounds...",
                "",
                0,
                PROGRESS_STEPS,
                self._ctx.main_window,
            )
            progress_bar.setWindowTitle("Generating...")
            progress_bar.setWindowModality(
                QtCore.Qt.WindowModality.WindowModal
            )
            progress_bar.setAutoClose(False)
            progress_bar.setMinimumDuration(0)
            progress_bar.setCancelButton(None)

            progress_bar.setValue(0)
            progress_bar.show()

            try:
                n_part_per_group = project.settings["n_allocations"] * [
                    project.settings["n_part_per_group"]
                ]
                fields = {
                    field_id: map_field_modes(field_usage)
                    for field_usage, field_ids in project.fields_usage.items()
                    for field_id in field_ids
                }
                settings = {
                    key: value
                    for key, value in project.settings.items()
                    if key not in ["n_part_per_group", "n_allocations"]
                }

                # Add pareto probabilities if algorithm is HERMES. Drop
                # probabilities for which the field is not set to mode
                # diversify.
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
                    progress_func=lambda fraction: progress_bar.setValue(
                        round(fraction * PROGRESS_STEPS)
                    ),
                    settings=settings,
                    return_full=True,
                    algorithm=algorithm,
                )
            except Exception as ex:
                progress_bar.close()
                QMessageBox.critical(
                    self, "Error", f"An error occurred during allocation: {ex}"
                )
                return
            else:
                people_data = project.pdata_mapped[project.fields_display()]
                ensemble = allocation_result.ensemble
                diversity_score = ensemble.calc_diversity_norm_score(
                    people_data
                )
                meeting_score = ensemble.calc_meeting_norm_score()

                # Close progress bar and display message box with results.
                progress_bar.close()
                QMessageBox.information(
                    self,
                    "Success!",
                    "The rounds were computed successfully.\n\n"
                    f"Diversity score: {diversity_score:.1%}\n"
                    f"Meeting score: {meeting_score:.1%}",
                )

                # Save the new allocations to the chosen setup, creating a
                # new one by default (see _refresh_setup_target).
                target_setup_idx = self._setup_target.currentData()
                if target_setup_idx is None:
                    setup = GSSetup(
                        project.next_setup_name(), project.next_id()
                    )
                    project.setups.append(setup)
                    target_setup_idx = len(project.setups) - 1
                else:
                    setup = project.setups[target_setup_idx]
                setup.add_allocations(
                    allocation_result.ensemble, project.next_id
                )

                project.selected_setup = target_setup_idx
                project.selected_allocation = None
                self._ctx.model_manager.updated_results()

                # Set project status to unsaved.
                self._ctx.set_unsaved()
        else:
            raise Exception("Unknown button pressed.")
