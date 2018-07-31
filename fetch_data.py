from __future__ import print_function

import billboard
import pandas as pd
import numpy as np
import json
import datetime


def get_df(chart_name, year):
    """Return dataframe with song, artist, title, date, and rank columns

    Fetch charts from current date until beginning of `year`
    """
    df = pd.DataFrame({'song': pd.Series([], dtype='str'),
                       'artist': pd.Series([], dtype='str'),
                       'title': pd.Series([], dtype='str'),
                       'date': pd.Series([], dtype='datetime64[ns]'),
                       'rank': pd.Series([], dtype='int')})
    i = 0
    chart = billboard.ChartData(chart_name, '{}-01-01'.format(year))
    while hasattr(chart, 'nextDate') and chart.nextDate[:4] == str(year):
        if i != 0:
            chart = billboard.ChartData(chart_name, date=chart.nextDate)
        print('week of {} retrieved'.format(chart.date))
        for song in chart:
            song_str = str(song)
            df.loc[i] = {'song': song_str,
                         'artist': song.artist,
                         'title': song.title,
                         'date': datetime.datetime.strptime(chart.date, '%Y-%m-%d').date(),
                         'rank': song.rank}
            i += 1
    return df


def write_linechart_json(df, fpath, cutoff=20):
    """Write data for chart.js line chart

    Parameters
    ----------
    df : pd.DataFrame
        dataframe with required columns song / date / rank
    fpath : str
        output filepath
    cutoff : int
        only include songs that have reached this ranking or higher.
    """
    # dates = np.flipud(df['date'].unique())
    dates = df['date'].unique()
    all_top10s = df.loc[df['rank'] <= cutoff, 'song'].unique()
    songs_group = df.groupby('song')

    data = {}
    data['labels'] = [str(v) for v in dates.astype('datetime64[D]')]
    data['datasets'] = []

    for song in all_top10s:
        df_song = songs_group.get_group(song)
        df_song.set_index('date', inplace=True)
        ds = {'label': song,
              'fill': False,
              'hidden': False,
              'pointHoverBackgroundColor': 'red',
              'data': [df_song.loc[date, 'rank']
                       if date in df_song.index else np.nan
                       for date in dates]}
        data['datasets'].append(ds)

    with open(fpath, 'w') as f:
        json.dump(data, f)


def generate_json_for(chart_name, year, cutoff=20):
    df = get_df(chart_name, year)
    fpath = 'docs/_data/{}_{}_top{}.json'.format(chart_name.replace('-', ''),
                                                 year, cutoff)
    write_linechart_json(df, fpath, cutoff)


if __name__ == '__main__':
    generate_json_for('hot-100', 2017)
