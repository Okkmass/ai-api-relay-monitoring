"""Regenerate chart.png from availability.csv.

Usage: python chart.py [path/to/availability.csv]   (needs matplotlib)
"""
import csv, collections, statistics, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from datetime import datetime

NAME = {"cc": "Claude", "cx": "GPT / Codex", "gm": "Gemini"}
COL = {"cc": "#4f46e5", "cx": "#059669", "gm": "#d97706"}
ok = collections.defaultdict(lambda: [0, 0]); lat = collections.defaultdict(list)
for r in csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "availability.csv")):
    k = (r["service"], r["probed_hour_utc"][:10]); s = int(r["status"])
    ok[k][1] += 1; ok[k][0] += s in (1, 2)
    if s in (1, 2): lat[k].append(int(r["latency_ms"]))
days = sorted({d for _, d in ok})
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#d4d4d8", "axes.labelcolor": "#27272a", "xtick.color": "#3f3f46", "ytick.color": "#3f3f46"})
fig, ax = plt.subplots(2, 1, figsize=(11, 7.2), dpi=160, sharex=True, gridspec_kw={"height_ratios": [1.15, 1]})
for svc in ("cc", "cx", "gm"):
    xs = [datetime.fromisoformat(d) for d in days if (svc, d) in ok]
    ax[0].plot(xs, [100 * ok[(svc, d)][0] / ok[(svc, d)][1] for d in days if (svc, d) in ok], color=COL[svc], lw=2, label=NAME[svc])
    ax[1].plot(xs, [statistics.median(lat[(svc, d)]) / 1000 for d in days if (svc, d) in lat], color=COL[svc], lw=2, label=NAME[svc])
ax[0].set_ylabel("Successful probes (%)"); ax[1].set_ylabel("Median latency (s)")
ax[0].set_title("AI API relays: daily success rate and latency by service", loc="left", fontsize=14, fontweight="bold", color="#18181b", pad=14)
for a in ax:
    a.grid(axis="y", color="#e4e4e7", lw=.8); a.spines[["top", "right"]].set_visible(False); a.tick_params(labelsize=10.5)
ax[0].legend(frameon=False, ncol=3, loc="lower left", fontsize=11)
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d")); ax[1].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
fig.text(0.01, 0.005, "Source: availability.csv (hourly probes, 72 anonymized stations, 2026-09-27 to 2026-11-01). Success = status 1 or 2. First and last day are partial.", fontsize=8.5, color="#52525b")
fig.tight_layout(rect=(0, .02, 1, 1)); fig.savefig("chart.png", facecolor="white")
