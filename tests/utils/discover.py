import importlib
import os


def scan_directory(path):
    for dir_name, subdir_list, file_list in os.walk(path):

        if not dir_name.startswith('./tests'):
            continue

        if '__init__.py' not in file_list:
            continue

        for file_name in file_list:
            if not file_name.endswith('.py'):
                continue

            path = '/'.join([dir_name, file_name])
            path = path[2:-3]  # trim ./ off front and .py off end
            path = path.replace('/', '.')

            importlib.import_module(path)
