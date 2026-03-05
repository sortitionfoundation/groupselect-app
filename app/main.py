#!/usr/bin/env python3
from pathlib import Path

from base_app.AppContext import AppContext

from GSProject import GSProject
from GSMainWindow import GSMainWindow
from GSModelManager import GSModelManager


RESOURCES_PATH: Path = Path(__file__).parent / "resources"


def main():
    app_ctx = AppContext(
        app_name='GroupSelect',
        app_version='v2.0.0',
        project_file_ending='.gspr',
        main_window_cls=GSMainWindow,
        model_manager_cls=GSModelManager,
        project_cls=GSProject,
        about_html_template=(RESOURCES_PATH / "about.html").read_text(encoding="utf-8")
    )
    app_ctx.launch()


if __name__ == '__main__':
    main()
