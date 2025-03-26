import logging 
import os
from typing import Optional
import yaml
from omegaconf import OmegaConf

LOG_FORMAT = "%(asctime)s\t%(threadName)s-%(name)s:%(levelname)s:%(message)s"
def setup_logger(name: str,
                 level: Optional[str] = None,
                 is_main: bool = False,
                 envvar_name: str = 'MOTPY_LOG_LEVEL'):
    if level is None:
        level = os.getenv(envvar_name)
        if level is None:
            level = 'DEBUG'
        else:
            print(f'[{name}] envvar {envvar_name} sets log level to {level}')

    level_val = logging.getLevelName(level)

    logger = logging.getLogger(name)
    logger.setLevel(level_val)
    logger.addHandler(logging.StreamHandler())
    
    if is_main:
        logging.basicConfig(filename="logging.log", level=level_val, format= LOG_FORMAT)
                            
    return logger


def config_module(name_module = __name__, config_path = "config.yaml"):
    """
    Configures the module settings for the application.
    
    """
    config = OmegaConf.load(config_path)
    config  = config[name_module]
   
    return config