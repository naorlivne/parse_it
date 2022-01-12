from pathlib import Path
from typing import Optional
import os
import warnings


def read_file(file_path: str) -> Optional[str]:
    """Read a file and returns it's contents (as a string) or None if file does not exist.

     Arguments:
        file_path -- the path of the file to be read
    Returns:
        file_contents -- string of the file contents
    """
    try:
        with open(file_path) as f:
            file_contents = f.read()
        return file_contents
    except FileNotFoundError:
        return None


def folder_exists(folder_path: str) -> bool:
    """Returns True if folder exists, False otherwise.

     Arguments:
        folder_path -- the path of the folder to be checked
    Returns:
        True if folder is dir, False otherwise
    """
    possible_folder = Path(strip_trailing_slash(folder_path))
    return possible_folder.is_dir()


def file_or_folder(checked_path: str) -> Optional[str]:
    """Returns "file" if the file_path is a file, "folder" if it's a dir & None otherwise.

     Arguments:
        checked_path -- the path of the file to be checked if it's a file or a folder
    Returns:
        "folder" if the path is a folder, "file" if it's a file and None otherwise
    """
    checked_file_path = Path(strip_trailing_slash(checked_path))
    if checked_file_path.is_dir() is True:
        return "folder"
    elif checked_file_path.is_file() is True:
        return "file"
    else:
        return None


def strip_trailing_slash(folder_path: str) -> str:
    """if a folder_path ends in a slash strip it & return the path, otherwise just return the path, only edge case is
        the root folder (/) which is kept the same.

     Arguments:
        folder_path -- the path of the folder to be checked
    Returns:
        A trailing slash stripped string of folder_path
    """
    if len(folder_path) > 1 and folder_path.endswith(("/", "\\")):
        folder_path = folder_path[:-1]
    return folder_path


def file_types_in_folder(folder_path: str, file_types_endings: list, recurse: bool = True) -> dict:
    """list all the config file types found inside the given folder based on the filename extension

        Arguments:
            folder_path -- the path of the folder to be checked
            file_types_endings -- list of file types to look for
            recurse -- if True (default) will also look in all subfolders
        Returns:
            config_files_dict -- dict of {file_type: [list_of_file_names_of_said_type]}
    """
    folder_path = strip_trailing_slash(folder_path)
    if folder_exists(folder_path) is False:
        warnings.warn("config_location " + folder_path + " does not exist, only envvars & cli args will be used")
        config_files_dict = {}
        for file_type_ending in file_types_endings:
            config_files_dict[file_type_ending] = []
    else:
        config_files_dict = {}
        for file_type_ending in file_types_endings:
            config_files_dict[file_type_ending] = []
            if recurse is True:
                for root, subFolders, files in os.walk(folder_path, topdown=True):
                    for file in files:
                        if file.endswith("." + file_type_ending):
                            if folder_path + "/" in root:
                                original_root_path = root
                                if root[0] != "/":
                                    root = root.split(folder_path + "/", 1)[1]
                                config_files_dict[file_type_ending].append(os.path.join(root, file))
                                if original_root_path != root:
                                    root = original_root_path
                            else:
                                config_files_dict[file_type_ending].append(file)
            else:
                for file in os.listdir(folder_path):
                    if os.path.isfile(os.path.join(folder_path, file)) and file.endswith(file_type_ending):
                        config_files_dict[file_type_ending].append(file)
            config_files_dict[file_type_ending].sort()
    return config_files_dict
