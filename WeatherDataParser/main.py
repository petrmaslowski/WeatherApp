import argparse
import time
from configuration import Configuration
from base_parser import BaseParser
from sensor_parser import SensorParser
from openweather_parser import OpenweatherParser

CONFIG_FILE = 'config.json'
SECRETS_FILE = 'secrets.json'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, default='sensor', help='sensor or openweather')
    return parser.parse_args()


def get_parser() -> BaseParser:
    config = Configuration(CONFIG_FILE, SECRETS_FILE)
    arguments = parse_args()

    if arguments.s == 'sensor':
        return SensorParser(config)
    elif arguments.s == 'openweather':
        return OpenweatherParser(config)
    else:
        raise ValueError('Invalid argument for -s: {}'.format(arguments.s))


def main_loop(data_parser: BaseParser):
    while True:
        try:
            data = data_parser.get_data()
            data_parser.write_data(data)
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print('Failed to fetch or save data: {}'.format(e))
        finally:
            time.sleep(data_parser.run_interval)


if __name__ == '__main__':
    parser = get_parser()
    main_loop(parser)
