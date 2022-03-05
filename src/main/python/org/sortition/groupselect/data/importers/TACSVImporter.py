import csv


def importFromCSV(file_lines: list, options: dict, numb_preview = None):
    if (options['delimiter'] == 'auto'):
        delimiter = __determineDelimiter(file_lines)
    else:
        delimiter = options['delimiter']

    iHeader = options['startLine']-1
    iStartRows = options['startLine']+options['skipLines']
    iEndRows = len(file_lines)-options['ignoreLast']

    if iHeader+1 > len(file_lines):
        return [], []

    lines_analyse = [file_lines[iHeader]]

    if iStartRows < iEndRows:
        if numb_preview is None or iEndRows - iStartRows < numb_preview:
            lines_analyse.extend(file_lines[iStartRows:iEndRows])
        else:
            lines_analyse.extend(file_lines[iStartRows:iStartRows+numb_preview])

    csv_reader = csv.reader(lines_analyse, delimiter=(';' if delimiter == 'semicolon' else ','))

    keys = list(next(csv_reader))
    vals = [row for row in csv_reader]

    return keys, vals


def __determineDelimiter(file_lines):
    N = 10
    contents = ''.join(file_lines[:N])
    ncs = contents.count(',')
    nss = contents.count(';')
    if (ncs < nss):
        return 'semicolon'
    else:
        return 'comma'