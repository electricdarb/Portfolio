import config
from csv_handle import csv_to_data
import googlemaps as gm
import numpy as np
import matplotlib.pyplot as plt
from time import time
import pandas as pd
from celluloid import Camera
import matplotlib.gridspec as gridspec

county_hash = pd.read_csv('county_hash.csv')
data = csv_to_data('us-counties.csv')

gmaps = gm.Client(key=config.key)

deaths_lat, deaths_lng, cases_lat, cases_lng = [type(np.empty(1))]* len(data), [type(np.empty(1))]* len(data),[type(np.empty(1))]* len(data), [type(np.empty(1))]* len(data)
c = 0 # day counter
for day in data:
    t1 = time()
    deaths_la, deaths_ln, cases_ln, cases_la = [], [], [], []
    for key in day.keys():
        latlng = (county_hash[key][0], county_hash[key][1])
        if latlng == (0, 0):
            continue
        try:
            leng = day[key][2]
        except ValueError:
            continue
        if leng > 0:
            cases_la += [latlng[0]] * leng
            cases_ln += [latlng[1]] * leng
        leng = day[key][3] # should work if day[key][2] works

        if leng > 0:
            deaths_la += [latlng[0]] * leng
            deaths_ln += [latlng[1]] * leng

    cases_lat[c] = np.array(cases_la)
    cases_lng[c] = np.array(cases_ln)
    deaths_lat[c] = np.array(deaths_la)
    deaths_lng[c] = np.array(deaths_ln)
    c += 1


fig = plt.figure(figsize=(9.33, 7.33))
gs = gridspec.GridSpec(6, 10, figure=fig)
ax = fig.add_subplot(gs[:4, :9])
bar = fig.add_subplot(gs[:4, 9])
daily = fig.add_subplot(gs[4:, :])
camera = Camera(fig)
ax.set_ylim(20, 55)
ax.set_xlim(-130, -60)
ax.axis('off')

fig.suptitle('90,000+ Americans Dead', fontsize = 16)
for o in ['top', 'right', 'bottom', 'left']:
    bar.spines[o].set_visible(False)
    daily.spines[o].set_visible(False)
daily.set_ylabel('Daily Deaths')
bar.set_ylabel('Total Dead Americans')
#bar.yaxis.set_label_position("right")
bar.yaxis.tick_right()
daily_deaths = []
months = ['january', 'febuary', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
month_ticks = [float]*12
month_ticks[0] = -21
for i in range(1, 12):
    month_ticks[i] = month_ticks[i-1] + 30.416
daily.set_xticks(month_ticks)
daily.set_xticklabels(months)
for i in range(len(cases_lng)):
    # making it so the dots dont overlap with each other
    cases_lng[i] += np.random.normal(0, .3, len(cases_lng[i]))
    cases_lat[i] += np.random.normal(0, .3, len(cases_lat[i]))
    deaths_lng[i] += np.random.normal(0, .3, len(deaths_lng[i]))
    deaths_lat[i] += np.random.normal(0, .3, len(deaths_lat[i]))
    daily_deaths.append(len(deaths_lng[i]))
    for j in range(1, i+2):
        cln = np.concatenate(cases_lng[0:j])
        cla = np.concatenate(cases_lat[0:j])
        dln = np.concatenate(deaths_lng[0:j])
        dla = np.concatenate(deaths_lat[0:j])
    ax.scatter(cln, cla, s=.03, c='b', label = 'Cases')
    ax.scatter(dln, dla, s=.03, c='r', label = 'Dead Americans')
    bar.bar(' ', len(dla), color = 'r')
    daily.plot(daily_deaths, c = 'r')
    camera.snap()
animation = camera.animate()
animation.save('animation.mp4')
plt.show()
