#!/bin/sh -e
### Config:
CSV_URL='http://wiki.creativecommons.org/Special:Ask/-5B-5Bdate::-3E2008-2D06-2D10-5D-5D-20-0A-20-20-5B-5BCategory::Event-5D-5D/%3FEventType/%3FDate/%3FLocation/%3FAttendance/%3FMainurl/%3FDivision/sort%3DDate/order%3DASC/format%3Dcsv/limit%3D1000'
FINAL_TEXTFILE_PATH="../textfile.txt"

### Code:
wget "$CSV_URL" -O- > input
PREFINAL_TEXTFILE_PATH="$(mktemp $FINAL_TEXTFILE_PATH.XXXXX)"
python csv2map.py >  "$PREFINAL_TEXTFILE_PATH"
mv "$PREFINAL_TEXTFILE_PATH" "$FINAL_TEXTFILE_PATH"
