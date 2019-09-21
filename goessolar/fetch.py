from __future__ import annotations
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from goessolar.kinds import Satellite, Product
from typing import Optional, List, Iterable
import numpy as np
import os

ROOT_URL = "https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes"


class CoverageSet:
    """
    An always growing set that stores contiguous datetimes. The purpose is to query if a datetime is covered by
    the data product or not.
    """
    def __init__(self):
        self.windows = set()

    def add(self, start: datetime, end: datetime) -> None:
        """
        Grow the coverage set by the new window (start, end)
        :param start: beginnning time
        :param end: ending time
        """
        # the CoverageSet is empty so just insert it
        if len(self.windows) == 0:
            self.windows.add((start, end))
        else:  # Coverage set is nonempty
            # the window is already covered
            if self.covers(start, end):
                return
            else:  # the window is not already covered

                # one of the existing windows partially covers the new window
                for window_start, window_end in self.windows:
                    if start <= window_start <= window_end <= end:
                        self.windows.remove((window_start, window_end))
                        self.windows.add((start, end))
                    elif start <= window_start <= end <= window_end:
                        self.windows.remove((window_start, window_end))
                        self.windows.add((start, window_end))
                    elif window_start <= start <= window_end <= end:
                        self.windows.remove((window_start, window_end))
                        self.windows.add((window_start, end))

                # none of the existing windows partially covers the new window
                self.windows.add((start, end))

    def __contains__(self, date: datetime) -> bool:
        """
        Determine if the specific date is in the coverage set
        :param date: query date
        :return: True if the coverage set includes the queried date
        """
        return any([start <= date <= end for start, end in self.windows])

    def covers(self, start: datetime, end: datetime) -> bool:
        """
        A window of the coverage set includes the entire start and end for this duration
        :param start: query beginning time
        :param end: query ending time
        :return: the duration between start and end is completely in the coverage set
        """
        return any([window_start <= start <= end <= window_end for window_start, window_end in self.windows])


def date_range(start, end) -> List[datetime]:
    # Truncate the hours, minutes, and seconds
    sdate: datetime = datetime(start.year, start.month, start.day)
    edate: datetime = datetime(end.year, end.month, end.day)

    # compute all dates in that difference
    delta: timedelta = sdate - edate
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


class Retriever:
    def __init__(self):
        self.catalog = {satellite: {product: None for product in Product} for satellite in Satellite}
        self.coverage = {satellite: {product: CoverageSet() for product in Product} for satellite in Satellite}

    @staticmethod
    def load(cls, path: str) -> Retriever:
        pass

    def save(self, path: str) -> None:
        pass

    @staticmethod
    def _format_url(satellite: Satellite, product: Product, date: datetime) -> str:
        satellite_str = str.lower(str(satellite).split(".")[1])
        product_str = str(product).split(".")[1].replace("_", "-")
        level = product_str.split("-")[1]
        date_str = date.strftime("%Y/%m/%d/")
        return "/".join([ROOT_URL, satellite_str, level, "data", product_str, date_str])

    @staticmethod
    def _fetch_page(url: str) -> pd.DataFrame:
        with urllib.request.urlopen(url) as response:
            html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        def split_entry(entry):
            contents = entry.find_all("td")
            file_name = contents[0].text
            date_edited = datetime.strptime(contents[1].text, '%Y-%m-%d %H:%M   ')
            date_begin = date_edited  # TODO: actually extract this from the filename
            file_size = contents[2].text
            return {'file_name': file_name, 'date_begin': date_begin,
                    'date_edited': date_edited, 'file_size': file_size, 'url': url + file_name}

        entries = soup.find_all('tr')[3:][:-1]
        results = list(map(split_entry, entries))
        df = pd.DataFrame(results)
        return df

    def fetch(self, directory: str, satellite: Iterable[Satellite], product: Iterable[Product],
              start: datetime, end: Optional[datetime] = None, count: int = 1, spaced: bool = False) -> None:
        if end is None:
            end = datetime(start.year, start.month, start.day, 23, 59, 59)
        for s in satellite:
            for p in product:
                self._fetch(directory, s, p, start, end, count=count, spaced=spaced)

    def _fetch(self, directory: str, satellite: Satellite, product: Product,
               start: datetime, end: datetime, count: int = 1, spaced: bool = False) -> None:

        # Make sure the catalog covers the required interval
        if not self.coverage[satellite][product].covers(start, end):
            dates = date_range(start, end)
            frames = map(lambda date: Retriever._fetch_page(Retriever._format_url(satellite, product, date)), dates)
            self.catalog[satellite][product] = pd.concat([self.catalog[satellite][product],
                                                          *frames]).drop_duplicates().reset_index(drop=True)

        # Select the required number of examples
        table = self.catalog[satellite][product]
        mask = (table['date_begin'] >= start) & (table['date_begin'] <= end)
        if spaced:
            selected = table[mask]['url'].values
            idx = np.round(np.linspace(0, len(selected) - 1, count)).astype(int)
            selected = selected[idx]
        else:  # get the nearest examples
            selected = table[mask]['url'].values[:count]

        # Download the examples
        for url in selected:
            urllib.request.urlretrieve(url, os.path.join(directory, url.split("/")[-1]))

