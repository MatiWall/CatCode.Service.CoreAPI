import yaml

from settings import BASE_DIR


def read_config():
    path = BASE_DIR/"configs"

    configs = []
    for file_path in path.glob("*.yaml"):
        with file_path.open("r") as config_file:
            file_config = yaml.safe_load(config_file)
            configs.append(file_config)
    return configs