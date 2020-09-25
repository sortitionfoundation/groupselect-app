#!/usr/bin/env python3
import sys
from org.sortition.groupselect.AppContext import AppContext

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
