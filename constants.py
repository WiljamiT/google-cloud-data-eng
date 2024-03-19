import configparser
import os

parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(__file__), 'config/config.local'))

YT_API_KEY = parser.get('youtube', 'API_KEY')