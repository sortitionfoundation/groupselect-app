from base_app.AppContext import AppContext

from src.GSProject import GSProject
from src.GSMainWindow import GSMainWindow
from src.GSModelManager import GSModelManager


def main():
    app_ctx = AppContext(
        app_name='GroupSelect',
        app_version='v2.0.0',
        project_file_ending='.gspr',
        main_window_cls=GSMainWindow,
        model_manager_cls=GSModelManager,
        project_cls=GSProject,
    )
    app_ctx.launch()


if __name__ == '__main__':
    main()
