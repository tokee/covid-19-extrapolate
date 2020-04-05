#!/usr/bin/env python3
#
# https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
#
# Usage: Run the script ./get_data.sh first, then this script

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load data [date deaths cumulative_deaths]
def load(data_path):
    file = open(data_path, 'r')
    entries = [line.strip() for line in file.readlines()]
    days = []
    deathss = []
    for day, e in enumerate(entries):
        if (e.startswith("#") or e == ""):
            continue
        date, deaths = e.split()
        days.append(day)
        deathss.append(int(deaths))
        last_date = date

    return np.array(days), np.array(deathss), last_date

x, y, last_date = load("denmark-deaths.dat")

# Fit the data to different formulas
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html

# Control from where we extrapolate and how far ahead we're looking
skip_days = 0
guess_days = 7

def func_exp(x, a, b, c):
    return a * np.exp(-b * x) + c
popt_exp, pcov_exp = curve_fit(func_exp, x, y)
perr_exp = np.sqrt(np.diag(pcov_exp))

def func_lin(x, a, b):
    return a + b*x
popt_lin, pcov_lin = curve_fit(func_lin, x, y)
perr_lin = np.sqrt(np.diag(pcov_lin))

def func_deg2(x, a, b, c):
    return a + b*x + c*x*x
popt_deg2, pcov_deg2 = curve_fit(func_deg2, x, y)
perr_deg2 = np.sqrt(np.diag(pcov_deg2))

def func_pow(x, a, b):
    return a*b**x
popt_pow, pcov_pow = curve_fit(func_pow, x[skip_days:], y[skip_days:], p0=(0, 1.1))
perr_pow = np.sqrt(np.diag(pcov_pow))

# Plot the data and the regressions
# Extend the regression lines this number of days ahead in the future

def label(format_str, popt, perr):
    reduced = [round(n, decimals) for n in popt]
    return format_str.format(*[round(n, decimals) for n in popt], [round(n, decimals) for n in perr])

plot_x = np.linspace(x[skip_days], max(x)+guess_days, 200)

decimals = 3
label_exp = label('{}*exp(-{}*x)+{}, spredning: {}', popt_exp, perr_exp)
label_lin = label('{}+{}*x, spredning: {}', popt_lin, perr_lin)
label_deg2 = label('{}+{}*x+{}*x^2, spredning: {}', popt_deg2, perr_deg2)
label_pow = label('{}*{}^x, spredning: {}', popt_pow, perr_pow)

plt.figure(dpi=180)
plt.title("Dødsfald med COVID-19-infektion, Danmark " + last_date)

axes = plt.gca()
axes.set_ylim([0, max(max(y), func_pow(max(x)+guess_days, *popt_pow))])
axes.set_xlim([0, max(x)+guess_days])

plt.plot(x, y, 'ko', label="Kumulative dødsfald")
plt.plot(plot_x, func_lin(plot_x, *popt_lin), 'r-', label=label_lin, color='blue')
#plt.plot(plot_x, func_exp(plot_x, *popt_exp), 'r-', label=label_exp, color='orange')
#plt.plot(plot_x, func_deg2(plot_x, *popt_deg2), 'r-', label=label_deg2, color='orange')
plt.plot(plot_x, func_pow(plot_x, *popt_pow), 'r-', label=label_pow, color='magenta')

plt.legend()
plt.figtext(0.99, 0.01, 'Datakilde: https://www.sst.dk/da/corona/tal-og-overvaagning', horizontalalignment='right')
#plt.show()

plt.savefig('covid-19-deaths-da-' + last_date + '.png')
