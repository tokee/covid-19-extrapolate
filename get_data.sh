#!/bin/bash

curl -s 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv' > hopkins-deaths.csv

head -n 1 hopkins-deaths.csv | sed 's/.*Long,//' | tr ',' '\n' | xargs -I {} -n 1 bash -c "date -d '{} -1 day' +%Y-%m-%d" > denmark-deaths-dates.dat
grep Denmark hopkins-deaths.csv | grep '^,Denmark' |  sed 's/,Denmark,56.2639,9.5018,//' | tr ',' '\n' > denmark-deaths-numbers.dat
paste denmark-deaths-dates.dat denmark-deaths-numbers.dat | grep -v '.*[^0-9]0$' > denmark-deaths.dat
