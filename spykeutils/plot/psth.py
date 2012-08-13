import scipy as sp
import quantities as pq

from guiqwt.builder import make
from guiqwt.baseplot import BasePlot
from guiqwt.plot import BaseCurveWidget

from dialogs import PlotDialog
import helper
from .. import rate_estimation
from ..spyke_exception import SpykeException
from ..progress_indicator import ProgressIndicator


def psth(trains, events, start, stop, bin_size, bar_plot,
         unit=pq.ms, progress=ProgressIndicator()):
    if not trains:
        raise SpykeException('No spike trains for PSTH!')

    if bar_plot:
        k = trains.keys()[0]
        trains = {k:trains[k]}

    # Align spike trains
    for u in trains:
        if events:
            trains[u] = rate_estimation.aligned_spike_trains(
                trains[u], events)
        else:
            trains[u] = trains[u].values()

    rates, bins = rate_estimation.psth(trains, bin_size, start=start,
        stop=stop)
    progress.done()

    if not psth:
        raise SpykeException('No spike trains for PSTH!')

    win_title = 'PSTH | Bin size %.2f %s' % (bin_size,
                                             unit.dimensionality.string)
    win = PlotDialog(toolbar=True, wintitle=win_title)

    if not bar_plot:
        bins = 0.5 * sp.diff(bins) + bins[:-1]

    pW = BaseCurveWidget(win)
    plot = pW.plot
    legend_items = []
    for i, r in rates.iteritems():
        if i and i.name:
            name = i.name
        else:
            name = 'Unknown'

        if not bar_plot:
            curve = make.curve(bins, r, name,
                color=helper.get_object_color(i))
            legend_items.append(curve)
            plot.add_item(curve)
        else:
            show_rates = list(r)
            show_rates.insert(0, show_rates[0])
            curve = make.curve(bins, show_rates, name, color='k',
                curvestyle="Steps", shade=1.0)
            plot.add_item(curve)
            break

    win.add_plot_widget(pW, 0)

    if not bar_plot:
        legend = make.legend(restrict_items=legend_items)
        plot.add_item(legend)
        win.add_legend_option([legend], True)

    plot.set_axis_title(BasePlot.Y_LEFT, 'Number of intervals')
    plot.set_axis_title(BasePlot.X_BOTTOM, 'Interval length')
    plot.set_axis_unit(BasePlot.X_BOTTOM, unit.dimensionality.string)
    win.add_custom_curve_tools()
    win.show()

    if bar_plot: # Rescale Bar plot
        scale = plot.axisScaleDiv(BasePlot.Y_LEFT)
        plot.setAxisScale(BasePlot.Y_LEFT, 0, scale.upperBound())
        plot.set_antialiasing(False)
    else:
        plot.set_antialiasing(True)