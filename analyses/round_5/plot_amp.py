"""Plot retained AMP pressure predictions for the same 105 measured states."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from present import HERE, load

MARKERS = {'loaded-pressure': ('Hartono original', 'o', '#236aa1'),
           'hartono-2021-supplemental': ('Hartono added', 's', '#a44d1a'),
           'tong': ('Tong added', '^', '#26826e')}


def plot():
    results = [load(f'A/{filename}.json.gz')['expanded']['rows'] for filename in
               ('original-main','expanded-free')]
    fig, axes = plt.subplots(1, 2, figsize=(7.2,3.5), layout='constrained', sharex=True, sharey=True)
    for label, ax, rows in zip(('Original calibration','Expanded calibration'), axes, results, strict=True):
        seen = []
        for group, (source, marker, color) in MARKERS.items():
            r = [r for r in rows if r['group']==group and r['prediction']['status']=='Available']
            seen.extend(r)
            ax.scatter([x['observed']/1000 for x in r], [x['prediction']['value']/1000 for x in r],
                       marker=marker, label=source, edgecolors=color, facecolors='none', s=14, linewidths=.9)
        assert len(seen)==105 and len({r['identity'] for r in seen})==105
        values = [r['observed']/1000 for r in seen] + [r['prediction']['value']/1000 for r in seen]
        lo,hi = min(values)*.84, max(values)*1.18
        ax.plot([lo,hi],[lo,hi],color='#4a4a4a',linestyle='--', linewidth=.8, zorder=0)
        ax.set(xscale='log',yscale='log',xlim=(lo,hi),ylim=(lo,hi),title=label,
               xlabel='Measured total pressure (kPa)', aspect='equal')
    axes[0].set_ylabel('Calculated total pressure (kPa)')
    axes[0].legend(loc='upper left',frameon=False,fontsize=8)
    fig.savefig(HERE/'AMP-loaded-pressure.png',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    plot()
