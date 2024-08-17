from dotenv import load_dotenv
from pyprojroot import here
from typing import List
import yaml
import os

load_dotenv()


class LoadConfig:
    # Class variable to track initialization
    _initialized = False

    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        # Data directories
        self.data_directory = app_config["directories"]["data_directory"]

        # Flask endpoint
        self.fastapi_endpoint = app_config["serve"]["fastapi_endpoint"]

        if not LoadConfig._initialized:
            # Clean up the upload doc vectordb if it exists
            self.create_directory([self.data_directory])

            # Set initialization flag to True
            LoadConfig._initialized = True

    @staticmethod
    def create_directory(dirs: List[str]):
        """
        Creates a directory if it does not exist.

        :param:
            dirs List[str]: The list of directories paths to be created
        """
        for directory in dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"The directory '{directory}' has been created.")
