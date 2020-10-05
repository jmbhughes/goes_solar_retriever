import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from goessolarretriever.kinds import Satellite, Product
from typing import Optional, List, Iterable
from tqdm import tqdm
import os
import numpy as np


ROOT_URL = "https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes"


def date_range(start, end):
    # Truncate the hours, minutes, and seconds
    sdate = datetime(start.year, start.month, start.day)
    edate = datetime(end.year, end.month, end.day)

    # compute all dates in that difference
    delta: timedelta = edate - sdate
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


class NameParser:
    suvi_ci = {Product.suvi_l2_ci094,
               Product.suvi_l2_ci131,
               Product.suvi_l2_ci171,
               Product.suvi_l2_ci195,
               Product.suvi_l2_ci284,
               Product.suvi_l2_ci304}

    suvi_lib = {Product.suvi_l1b_fe094,
                Product.suvi_l1b_fe131,
                Product.suvi_l1b_fe171,
                Product.suvi_l1b_fe195,
                Product.suvi_l1b_fe284,
                Product.suvi_l1b_he304}

    def __init__(self, satellite: Satellite, product: Product):
        self.satellite = satellite
        self.product = product

    def get_dates(self, name):
        """
        Overall method to get the date and time from a filename string
        :param name: filename extracted from web page
        :return: start and end times of the observation
        """
        if self.product in NameParser.suvi_ci:
            return NameParser._get_dates_suvi_ci(name)
        elif self.product in NameParser.suvi_lib:
            return NameParser._get_dates_suvi_l1b(name)
        else:
            return None, None

    @staticmethod
    def _get_dates_suvi_ci(name):
        """
        Filename parser for Suvi Composite Image data
        :param name: filename
        :return: start and end date
        """
        _, product_str, satellite_str, start_str, end_str, _ = name.split("_")
        start = datetime.strptime(start_str, "s%Y%m%dT%H%M%SZ")
        end = datetime.strptime(end_str, "e%Y%m%dT%H%M%SZ")
        return start, end

    @staticmethod
    def _get_dates_suvi_l1b(name):
        """
        Filename parser for Suvi Composite Image data
        :param name: filename
        :return: start and end date
        """
        _, product_str, satellite_str, start_str, end_str, _ = name.split("_")
        start = datetime.strptime(start_str[:-1], "s%Y%j%H%M%S")
        end = datetime.strptime(end_str[:-1], "e%Y%j%H%M%S")
        return start, end


class Retriever:
    def __init__(self):
        pass

    @staticmethod
    def load(cls, path):
        pass

    def save(self, path) -> None:
        pass

    @staticmethod
    def _format_url(satellite: Satellite, product: Product, date: datetime) -> str:
        satellite_str = str.lower(str(satellite).split(".")[1])
        product_str = str(product).split(".")[1].replace("_", "-")
        level = product_str.split("-")[1]
        date_str = date.strftime("%Y/%m/%d/")
        return "/".join([ROOT_URL, satellite_str, level, "data", product_str, date_str])

    @staticmethod
    def _fetch_page(url: str, parser):
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
            soup = BeautifulSoup(html, 'html.parser')

            def split_entry(entry):
                contents = entry.find_all("td")
                file_name = contents[0].text
                date_edited = datetime.strptime(contents[1].text, '%Y-%m-%d %H:%M   ')
                date_begin, date_end = parser.get_dates(file_name)
                file_size = contents[2].text
                return {'file_name': file_name, 'date_begin': date_begin, 'date_end': date_end,
                        'date_edited': date_edited, 'file_size': file_size, 'url': url + file_name}

            entries = soup.find_all('tr')[3:][:-1]
            results = list(map(split_entry, entries))
            df = pd.DataFrame(results)
        except urllib.request.HTTPError:
            df = pd.DataFrame()
        return df

    def search(self, satellite: Satellite, product,
               start, end=None):
        if end is None:
            end = datetime(start.year, start.month, start.day, 23, 59, 59)

        results = pd.DataFrame()
        for day in date_range(start, end):
            name_parser = NameParser(satellite, product)
            url = Retriever._format_url(satellite, product, day)
            page = Retriever._fetch_page(url, name_parser)
            results = pd.concat([results, page], ignore_index=True)
        return results

    def retrieve(self, results, save_directory):
        for _, row in tqdm(results.iterrows()):
            try:
                urllib.request.urlretrieve(row['url'], os.path.join(save_directory, row['file_name']))
            except ValueError:
                pass

    def retrieve_nearest(self, satellite, product, date, save_directory):
        df = self.search(satellite, product, date)
        try:
            best_index = np.argmin(np.abs(df['date_begin'] - date))
        except KeyError:
            raise RuntimeError("Data does not exist for the time {}".format(date))
        self.retrieve(df.iloc[[best_index]], save_directory)
        return os.path.join(save_directory, df.iloc[best_index]['file_name'])
