
import pandas as pd
import requests
from pandas import DataFrame

from base_parser import BaseParser
from configuration import Configuration


class OpenweatherParser(BaseParser):
    def __init__(self, config: Configuration):
        super().__init__(config)

        self.measurement = config.openweather_calculation['measurement']
        self.run_interval = config.openweather_calculation['run_interval']

    def get_data(self) -> DataFrame:
        response = requests.get(self.config.openweathermap_url, params=self.config.openweathermap_params)

        if response.status_code == 200:

            data = response.json()
            timezone = data['timezone']
            data_frame = pd.json_normalize(data['current'])
            data_frame = data_frame.drop(columns=['weather'], errors='ignore')
            data_frame = data_frame.astype(float)
            for key in ['dt', 'sunrise', 'sunset']:
                data_frame[key] = pd.to_datetime(data_frame[key], unit='s').dt.tz_localize('UTC').dt.tz_convert(timezone)
            data_frame = data_frame.set_index('dt')
            data_frame.index.name = 'time'

            return data_frame
