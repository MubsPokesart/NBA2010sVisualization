import os
from dotenv import load_dotenv
load_dotenv()

dirname = os.path.dirname(__file__)
os.environ["KAGGLE_CONFIG_DIR"] = os.path.join(dirname, 'kaggle')
print(os.environ.get('KAGGLE_USERNAME'))

print(os.environ.get('KAGGLE_CONFIG_DIR'))
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
# Get attributes of the KaggleApi object
print(api.config)
print(os.path.exists(api.config))
print(api.get_config_value(api.CONFIG_NAME_USER))

api.dataset_metadata('wyattowalsh/basketball', path=os.path.join(dirname, 'temp'))