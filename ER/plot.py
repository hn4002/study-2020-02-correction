import pandas
import matplotlib.pyplot as plt

er_stats_all = pandas.read_csv("ER_stats.csv")
er_stats_all.head()

er_stats = er_stats_all[['ER', 'Avg.Correction', 'Avg.Advance', 'Avg.Recovery']]
er_stats.head()

ax = er_stats.plot(title="EPS Rating Study", x="ER", figsize=(15, 9), grid=True, legend=True)
# ax is of type matplotlib.axes.AxesSubplot
ax.set_ylabel("% Change")
ax.set_xlabel("EPS Rating")
plt.savefig("epsplot.png")
plt.show()
