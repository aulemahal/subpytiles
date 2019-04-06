"""Subpytles

Class to store srt subtitles and manage them.
"""
import datetime as dt
import pandas as pd


class Subtitles(object):
    """Subtitles

    Main class to play with subtitle files.
    """

    def __init__(self, subtitles):
        self.data = subtitles

    @classmethod
    def read_srt(cls, filename):
        """Read subtitles from a srt file.

        Arguments:
            filename {str} -- The srt file
        """
        data = pd.DataFrame(columns=['begins', 'ends', 'text'])
        with open(filename, 'r', errors='ignore') as srtfile:
            for line in map(str.strip, srtfile):
                sub = []
                while len(line) > 0:
                    sub.append(line)
                    line = srtfile.readline().strip()
                if sub:
                    try:
                        data.loc[int(sub[0])] = [*map(lambda x: dt.datetime.strptime(x.strip() + '000', '%H:%M:%S,%f'), sub[1].split('-->'))] + ['\n'.join(sub[2:])]
                    except (ValueError, TypeError) as err:
                        print(f"Malformed srt element : {' | '.join(sub)}")
                        print(err)
        return cls(data)

    def shift(self, timedelta):
        if isinstance(timedelta, str):
            timedelta = dt.datetime.strptime(timedelta + '000', '%H:%M:%S,%f') - dt.datetime.strptime('00:00:00,000000', '%H:%M:%S,%f')
        elif isinstance(timedelta, (int, float)):
            timedelta = dt.timedelta(seconds=timedelta)
        self.data.begins += timedelta
        self.data.ends += timedelta

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError(f'Addition to type {type(other)} not yet implemented.')
        return Subtitles(pd.concat((self.data, other.data), ignore_index=True).sort_values('begins').reset_index(drop=True))

    def to_srt(self, filename):
        with open(filename, 'w') as srtfile:
            for i, row in self.data.iterrows():
                srtfile.writelines([str(i), '\n',
                                    row.begins.strftime('%H:%M:%S,%f')[:-3], ' --> ', row.ends.strftime('%H:%M:%S,%f')[:-3], '\n',
                                    row.text, '\n\n'
                                    ])
