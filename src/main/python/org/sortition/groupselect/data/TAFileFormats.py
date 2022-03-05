base_types_files = [
    ('GroupSelect 2 Files', '*.gsf2'),
    #('OpenDocument spreadsheet', '*.ods'),     # currently not implemented
    ('Excel files', '*.xls *.xlsx'),
    ('Comma-separated values files', '*.csv *.tsv'),
]

base_types_import = base_types_files[1:]
base_types_files_save = base_types_files[0:1]

def __convertFormats(base_types: list):
    return ';;'.join(
        [f"All allowed file formats ({' '.join(ending for _, ending in base_types)})"] +
        [f"{name} ({endings})" for name, endings in base_types]
    )

file_formats = __convertFormats(base_types_files)
import_formats = __convertFormats(base_types_import)
save_formats = __convertFormats(base_types_files_save)