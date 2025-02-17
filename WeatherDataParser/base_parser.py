
from abc import ABC, abstractmethod
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from pandas import DataFrame

from configuration import Configuration


class BaseParser(ABC):
    def __init__(self, config: Configuration):
        self.config = config
        db_client = InfluxDBClient(url=self.config.db_url,
                                   token=self.config.db_token,
                                   org=self.config.db_org)
        self.write_api = db_client.write_api(write_options=SYNCHRONOUS)
        self.delete_api = db_client.delete_api()
        self.measurement = None
        self.run_interval = None

    @abstractmethod
    def get_data(self) -> DataFrame:
        pass

    def write_data(self, data: DataFrame):
        self.write_api.write(bucket=self.config.db_name, org=self.config.db_org, write_precision='s', record=data, data_frame_measurement_name=self.measurement)

    def delete_data(self):
        self.delete_api.delete("1970-01-01T00:00:00Z", "2030-01-01T00:00:00Z", '_measurement=' + self.measurement, bucket=self.config.db_name, org=self.config.db_org)
