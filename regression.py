#!/usr/bin/env python3
#
# https://stackoverflow.com/questions/3433486/how-to-do-exponential-and-logarithmic-curve-fitting-in-python-i-found-only-poly
#
# Usage: Run the script ./get_data.sh first, then this script

# TODO: Make downloading of data part of this script

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# TODO: Make this an option
country = 'Denmark'

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

#x, y, last_date = load("Denmark-deaths.dat")
x, y, last_date = load(country + "-deaths.dat")

# Fit the data to different formulas
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html

# Control from where we extrapolate and how far ahead we're looking
# TODO: Make these options
skip_days = 0
guess_days = 14
# Used by pow_last2 to extrapolate from the last x days
last_days = 7

x_fit = x[skip_days:]
y_fit = y[skip_days:]

def func_exp(x, a, b, c):
    return a * np.exp(-b * x) + c
popt_exp, pcov_exp = curve_fit(func_exp, x_fit, y_fit)
perr_exp = np.sqrt(np.diag(pcov_exp))

def func_lin(x, a, b):
    return a + b*x
popt_lin, pcov_lin = curve_fit(func_lin, x_fit, y_fit)
perr_lin = np.sqrt(np.diag(pcov_lin))

def func_deg2(x, a, b, c):
    return a + b*x + c*x*x
popt_deg2, pcov_deg2 = curve_fit(func_deg2, x_fit, y_fit)
perr_deg2 = np.sqrt(np.diag(pcov_deg2))

def func_pow(x, a, b):
    return a*b**x
popt_pow, pcov_pow = curve_fit(func_pow, x_fit, y_fit, p0=(0, 1.1))
perr_pow = np.sqrt(np.diag(pcov_pow))

def func_pow2(x, y0, a, b):
    return y0+a*b**x
popt_pow2, pcov_pow2 = curve_fit(func_pow2, x_fit, y_fit, p0=(1, 0, 1.1))
perr_pow2 = np.sqrt(np.diag(pcov_pow2))

x_fit_last = x[-last_days:]
y_fit_last = y[-last_days:]
def func_pow_last2(x, y0, a, b):
    return y0+a*b**x
popt_pow_last2, pcov_pow_last2 = curve_fit(func_pow_last2, x_fit_last, y_fit_last, p0=(1, 0, 1.1))
perr_pow_last2 = np.sqrt(np.diag(pcov_pow_last2))
plot_x_last = np.linspace(x_fit_last[0], max(x_fit_last)+guess_days, 200)


# Plot the data and the regressions
# Extend the regression lines this number of days ahead in the future

def label(format_str, popt, perr):
    return format_str.format(*[round(n, 2) for n in popt], [round(n, 3) for n in perr])

plot_x = np.linspace(x_fit[0], max(x_fit)+guess_days, 200)

label_exp = label('{}exp(-{}x)+{}, spredning: {}', popt_exp, perr_exp)
label_lin = label('{}+{}x, spredning: {}', popt_lin, perr_lin)
label_deg2 = label('{}+{}x+{}x², spredning: {}', popt_deg2, perr_deg2)
label_pow = label('{}*{}ˣ, spredning: {}', popt_pow, perr_pow)
label_pow2 = label('{}+{}*{}ˣ, spredning: {}', popt_pow2, perr_pow2)
label_pow_last2 = label('{}+{}*{}ˣ, spredning: {}', popt_pow_last2, perr_pow_last2)

plt.figure(dpi=180)
plt.title("Dødsfald med COVID-19-infektion, " + country + " " + last_date)

axes = plt.gca()
axes.set_ylim([0, max(max(y), func_pow(max(x)+guess_days, *popt_pow))])
axes.set_xlim([0, max(x)+guess_days])

plt.plot(x, y, 'ko', label="Kumulative dødsfald")
#plt.plot(plot_x, func_lin(plot_x, *popt_lin), 'r-', label=label_lin, color='blue')
#plt.plot(plot_x, func_exp(plot_x, *popt_exp), 'r-', label=label_exp, color='orange')
#plt.plot(plot_x, func_deg2(plot_x, *popt_deg2), 'r-', label=label_deg2, color='orange')
plt.plot(plot_x, func_pow(plot_x, *popt_pow), 'r-', label=label_pow, color='green')
#plt.plot(plot_x, func_pow2(plot_x, *popt_pow2), 'r-', label=label_pow2, color='magenta')
#plt.plot(plot_x_last, func_pow_last2(plot_x_last, *popt_pow_last2), 'r-', label=label_pow_last2, color='orange')

plt.legend()
# https://www.sst.dk/da/corona/tal-og-overvaagning
plt.figtext(0.99, 0.01, 'Datakilde: https://github.com/CSSEGISandData/COVID-19', horizontalalignment='right')
#plt.show()

plt.savefig('covid-19-deaths-' + country + '-' + last_date + '.png')
