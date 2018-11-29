import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, PathPatch
import pymap3d as pm
from satellite.conversions import azimuth_to_theta, elevation_to_radius


from satellite import conversions


def plot_az_el(az, el):
    figure = plt.figure(figsize=(5.2, 4.0))

    visible, invisible = split_visible_points(az, el)

    points_color = {
        'b': az_el_to_theta_radius(visible),
        'r': az_el_to_theta_radius(invisible),
    }

    ax = plt.subplot(projection='polar')

    for color, points in points_color.items():
        if not points:
            continue
        x, y = list(zip(*points))
        ax.plot(x, y, marker='o', linestyle='', ms=2, color=color, alpha=0.75)
    first_last = az_el_to_theta_radius([(az[i], el[i]) for i in [0, -1]])
    x = [point[0] for point in first_last]
    y = [point[1] for point in first_last]
    ax.plot(x, y, marker='o', linestyle='', ms=3, color='black', alpha=0.75)
    ax.plot(azimuth_to_theta(0), elevation_to_radius(-15), linestyle='', ms=1, color='grey', alpha=0.1)

    ax.set_rticks([30, 60, 90])

    labels = [item.get_text() for item in ax.get_yticklabels()]
    empty_string_labels = [''] * len(labels)
    ax.set_yticklabels(empty_string_labels)

    TICK_SIZE = 7
    ax.set_xticklabels(['East', '', 'North', '', 'West', '', 'South', ''], fontsize=TICK_SIZE)

    XTICK_PAD = 0.1
    ax.tick_params(axis='both', which='major', pad=XTICK_PAD)

    FONT_SIZE = 9.0
    Y_LABELPAD = 65
    X_LABELPAD = 8
    ax.set_xlabel('Azimuth [0, 360]º', fontsize=FONT_SIZE, labelpad=X_LABELPAD)
    ax.set_ylabel('Elevation [-90, 90]º', fontsize=FONT_SIZE,
                  labelpad=Y_LABELPAD)


    circle = Circle((0, 0), 180, transform=ax.transData._b, color='grey',
                    alpha=0.5)
    ax.add_artist(circle)

    circle = Circle((0, 0), 90, transform=ax.transData._b, color='white')
    ax.add_artist(circle)


    invisible_area = mpatches.Patch(color='grey', label='Invisible area')

    plt.legend(loc='upper center', handles=[invisible_area], bbox_to_anchor=(0.95, 1.1))
    PATCH_LEGEND_SIZE = 9.5
    plt.rcParams["legend.fontsize"] = PATCH_LEGEND_SIZE


    for i in [0, 30, 60, 90, -30]:
        x = conversions.azimuth_to_theta(45)
        y = conversions.elevation_to_radius(i)
        ax.annotate(str(i), xy=(x, y))

    if len(az) > 1:
        ax.annotate('   Start', first_last[0])
        ax.annotate('   End', first_last[1])
    else:
        ax.annotate('   Start/End', first_last[0])
    return figure



def annotate_satellite(ax, az, el, dates):
    for i in range(len(az)):
        x = conversions.azimuth_to_theta(az[i])
        y = conversions.elevation_to_radius(el[i])
        xy = (x, y)

        label = '  {}'.format(i + 1)
        ax.annotate(label, xy, fontsize=12)

    points = list(zip(az, el, dates))
    df = pd.DataFrame(points, index=[i for i in range(1, len(points) + 1)],
                      columns=['Azimuth', 'Elevation', 'Time'])
    return df

def see_satellite(satellite, obs_lat, obs_lon, obs_alt, start, end, count=None, annotate=True, title=''):
    positions_at = satellite.propagate_positions(start, end, count=count)

    azimuth = []
    elevation = []
    dates = []

    for position_at in positions_at:
        eci, date = position_at
        aer = pm.eci2aer(eci, obs_lat, obs_lon, obs_alt, date)
        az = aer[0][0]
        el = aer[1][0]

        azimuth.append(az)
        elevation.append(el)
        dates.append(date)

    print('plotted points between [{}] and [{}].'.format(dates[0], dates[-1]))

    plot_az_el(azimuth, elevation)
    dates = [x[1] for x in positions_at]
    ax = plt.gca()

    plt.suptitle(title, size=20)

    df = pd.DataFrame({'Azimuth': azimuth,
                       'Elevation': elevation,
                       'Date': dates})
    return df


def split_visible_points(x, y):
    visible = []
    invisible = []

    for i, yi in enumerate(y):
        point = (x[i], yi)
        if conversions.is_point_visible(yi):
            visible.append(point)
        else:
            invisible.append(point)
    return visible, invisible


def az_el_to_theta_radius(az_el):
    theta_radius = tuple(
        (conversions.azimuth_to_theta(x), conversions.elevation_to_radius(y)) for x, y in az_el)
    return theta_radius
