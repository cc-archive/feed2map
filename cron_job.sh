#!/bin/sh -e
### Config:
BASE_PATH="/home/paulproteus/events-map/cclearn-events-map/"
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
# DONE: CSV_URL includes today's date!
CSV_URL="http://opened.creativecommons.org/Special:Ask/-5B-5Bdate::-3E$YEAR-2D$MONTH-2D$DAY-5D-5D-20-0A-20-20-5B-5BCategory::Event-5D-5D/%3FEventType/%3FDate/%3FLocation/%3FAttendance/%3FMainurl/%3FEventCategory/sort%3DDate/order%3DASC/format%3Dcsv/limit%3D1000"
FINAL_TEXTFILE_PATH="/home/paulproteus/events-map/textfile.txt"

### Code:
cd "$BASE_PATH"
wget -q "$CSV_URL" -O- > input
PREFINAL_TEXTFILE_PATH="$(mktemp $FINAL_TEXTFILE_PATH.XXXXX)"
chmod 644 "$PREFINAL_TEXTFILE_PATH"
python csv2map.py >  "$PREFINAL_TEXTFILE_PATH"
mv "$PREFINAL_TEXTFILE_PATH" "$FINAL_TEXTFILE_PATH"
