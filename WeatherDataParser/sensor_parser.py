
import bme680
import datetime
import pandas as pd
import time
from bme680 import BME680
from pandas import DataFrame

from base_parser import BaseParser
from configuration import Configuration


class SensorParser(BaseParser):
    def __init__(self, config: Configuration):
        super().__init__(config)

        self.humidity_baseline = config.sensor_calculation['humidity_baseline']
        self.humidity_weight = config.sensor_calculation['humidity_weight']
        self.calibration_time = config.sensor_calculation['calibration_time']
        self.measurement = config.sensor_calculation['measurement']
        self.run_interval = config.sensor_calculation['run_interval']
        self.sensor = self._get_sensor()
        self.gas_baseline = self._calibrate_sensor()

    def get_data(self) -> DataFrame:

        if self.sensor.get_sensor_data():
            timestamp = int(datetime.datetime.now().timestamp())
            dataframe = pd.DataFrame({
                'temp': self.sensor.data.temperature,
                'pressure': self.sensor.data.pressure,
                'humidity': self.sensor.data.humidity,
                'gas_resistance': None,
                'air_quality': None},
                index=[timestamp])
            dataframe.index.name = 'time'

            if self.sensor.data.heat_stable:
                gas = self.sensor.data.gas_resistance
                dataframe.loc[timestamp, 'gas_resistance'] = gas

                gas_offset = self.gas_baseline - gas

                humidity = self.sensor.data.humidity
                hum_offset = humidity - self.humidity_baseline

                if hum_offset > 0:
                    hum_score = (100 - self.humidity_baseline - hum_offset)
                    hum_score /= (100 - self.humidity_baseline)
                    hum_score *= (self.humidity_weight * 100)

                else:
                    hum_score = (self.humidity_baseline + hum_offset)
                    hum_score /= self.humidity_baseline
                    hum_score *= (self.humidity_weight * 100)

                if gas_offset > 0:
                    gas_score = (gas / self.gas_baseline)
                    gas_score *= (100 - (self.humidity_weight * 100))

                else:
                    gas_score = 100 - (self.humidity_weight * 100)

                air_quality = hum_score + gas_score
                dataframe.loc[timestamp, 'air_quality'] = round(air_quality, 2)

            return dataframe

    def _get_sensor(self) -> BME680:
        try:
            sensor = BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            sensor = BME680(bme680.I2C_ADDR_SECONDARY)

        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)

        return sensor

    def _calibrate_sensor(self) -> float:
        start_time = time.time()
        curr_time = time.time()
        calibration_data = []

        while curr_time - start_time < self.calibration_time:
            curr_time = time.time()
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                gas = self.sensor.data.gas_resistance
                calibration_data.append(gas)
                time.sleep(1)

        return sum(calibration_data[-50:]) / 50.0
