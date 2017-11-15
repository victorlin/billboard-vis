from __future__ import print_function

import billboard
import pandas as pd
import numpy as np
import json


def get_df(chart_name, year):
    """Return dataframe with song, date, rank columns

    Fetch charts from current date until beginning of `year`
    """
    df = pd.DataFrame({'song': pd.Series([], dtype='str'),
                       'date': pd.Series([], dtype='datetime64[ns]'),
                       'rank': pd.Series([], dtype='int')})
    i = 0
    chart = billboard.ChartData(chart_name)
    # while chart.previousDate[:4] == str(year):
    for j in range(2):
        if i != 0:
            chart = billboard.ChartData(chart_name, date=chart.previousDate)
        print('fetching data for week of', chart.date_str)
        for song in chart:
            song_str = str(song)
            df.loc[i] = {'song': song_str,
                         'date': chart.date,
                         'rank': song.rank}
            i += 1
    return df


def write_json(df, fpath):
    """Write data for chart.js

    Subset: only include songs that have reached top 10 ranking.
    """
    dates = np.flipud(df['date'].unique())
    all_top10s = df.loc[df['rank'] <= 10, 'song'].unique()
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

df = get_df('hot-100', 2017)
write_json(df, 'docs/_data/hot100_2017_top10s.json')
