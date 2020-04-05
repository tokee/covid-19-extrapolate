#!/bin/bash

: ${COUNTRY:="Denmark"}

curl -s 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv' > hopkins-deaths.csv

head -n 1 hopkins-deaths.csv | sed 's/.*Long,//' | tr ',' '\n' | xargs -I {} -n 1 bash -c "date -d '{} -1 day' +%Y-%m-%d" > ${COUNTRY}-deaths-dates.dat
grep ${COUNTRY} hopkins-deaths.csv | grep "^,${COUNTRY}" |  sed "s/,${COUNTRY},[-0-9.]*,[-0-9.]*,//" | tr ',' '\n' > ${COUNTRY}-deaths-numbers.dat
paste ${COUNTRY}-deaths-dates.dat ${COUNTRY}-deaths-numbers.dat | grep -v '.*[^0-9]0$' > ${COUNTRY}-deaths.dat
