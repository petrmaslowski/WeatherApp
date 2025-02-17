
import json


class Configuration:
    def __init__(self, config_file: str, secrets_file: str):
        try:
            self.config = json.load(open(config_file, mode='r'))
            self.secrets = json.load(open(secrets_file, mode='r'))
        except FileNotFoundError as e:
            print('FileNotFoundError: {}'.format(e))
            exit(1)

    @property
    def db_url(self) -> str:
        return str(self.config['db']['host']) + ':' + str(self.config['db']['port'])

    @property
    def db_name(self) -> str:
        return self.config['db']['name']

    @property
    def db_org(self) -> str:
        return self.config['db']['org']

    @property
    def db_token(self) -> str:
        return self.secrets['influxdb_token']

    @property
    def db_openweather_measurement(self) -> str:
        return self.config['db']['openweather_measurement']

    @property
    def db_sensor_measurement(self) -> str:
        return self.config['db']['sensor_measurement']

    @property
    def openweathermap_config(self) -> dict:
        return self.config['openweathermap']

    @property
    def openweathermap_url(self) -> str:
        return self.config['openweathermap']['url']

    @property
    def openweathermap_params(self) -> dict:
        params = self.config['openweathermap']['params']
        params['appid'] = self.secrets['openweathermap_appid']
        return params

    @property
    def sensor_calculation(self) -> dict:
        return self.config['sensor_calculation']

    @property
    def openweather_calculation(self) -> dict:
        return self.config['openweather_calculation']
