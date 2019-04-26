from pathlib import Path
import os


def read_file(file_path):
    """Read a file and returns it's contents (as a string) or None if file does not exist.

     Arguments:
    file_path -- the path of the file to be read
    """
    try:
        with open(file_path) as f:
            file_contents = f.read()
        return file_contents
    except FileNotFoundError:
        return None


def folder_exists(folder_path):
    """Returns True if folder exists, False otherwise.

     Arguments:
    folder_path -- the path of the folder to be checked
    """
    possible_folder = Path(strip_trailing_slash(folder_path))
    return possible_folder.is_dir()


def strip_trailing_slash(folder_path):
    """if a folder_path ends in a slash strip it & return the path, otherwise just return the path, only edge case is
        the root folder (/) which is kept the same.

     Arguments:
    folder_path -- the path of the folder to be checked
    """
    if len(folder_path) > 1 and folder_path[-1] == "/" or folder_path[-1] == "\\":
        folder_path = folder_path[:-1]
    return folder_path


def file_types_in_folder(folder_path, file_types_endings):
    """list all the config file types found inside the given folder based on the filename extension

        Arguments:
            folder_path -- the path of the folder to be checked
            file_types_endings -- list of file types to look for
        Returns:
            config_files_dict -- dict of {file_type: [list_of_file_names_of_said_type]}
    """
    folder_path = strip_trailing_slash(folder_path)
    if folder_exists(folder_path) is False:
        raise FileNotFoundError
    else:
        config_files_dict = {}
        for file_type_ending in file_types_endings:
            config_files_dict[file_type_ending] = []
            for root, subFolders, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(file_type_ending):
                        config_files_dict[file_type_ending].append(file)
        return config_files_dict
