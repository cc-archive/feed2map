#!/bin/sh
PASSWORD="$(cat password)"
exec wget -q "http://ccidonor:$PASSWORD@ccidonor.civicactions.net/v7VILBpo26ww?contribDate=2007-07-01" -O input
