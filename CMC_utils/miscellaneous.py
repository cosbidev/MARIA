import os
import torch
import random
import inspect
import logging
import numpy as np
import pandas as pd
from omegaconf import DictConfig, OmegaConf
from typing import Any, Union, Tuple


log = logging.getLogger(__name__)

__all__ = ["seed_all", "seed_worker", "filter_kwargs", "recursive_cfg_substitute", "recursive_cfg_search", "join_dictionaries", "join_preprocessing_params", "longest_common_substring", "do_nothing", "do_really_nothing", "play_sound"]


def seed_all( seed: int = 42 ) -> None:
    """
    This function sets the seed for all the packages used in the project.
    Parameters
    ----------
    seed : int

    Returns
    -------
    None
    """
    np.random.seed( seed )
    random.seed( seed )
    torch.manual_seed( seed )
    torch.cuda.empty_cache()
    torch.cuda.manual_seed_all(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    log.debug(f"Seed set to {seed}")


def seed_worker( worker_id ) -> None:
    """
    This function sets the seed for the worker.
    Parameters
    ----------
    worker_id : int

    Returns
    -------
    None
    """
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed( worker_seed )
    random.seed( worker_seed )


def filter_kwargs(func, **kwargs):
    # Inspect the function's signature to find out what parameters it can accept
    sig = inspect.signature(func)
    # Filter the kwargs to only include those that the function can accept
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return filtered_kwargs


def recursive_cfg_substitute(original_dict: Union[dict, DictConfig], substitution_dict: dict) -> Union[dict, DictConfig]:
    """
    This function substitutes the values of the keys in the original dictionary with the values of the keys in the substitution dictionary.
    Parameters
    ----------
    original_dict : dict
    substitution_dict : dict

    Returns
    -------
    dict
    """
    for key in original_dict:
        if type(original_dict[key]) in (dict, DictConfig):
            original_dict[key] = recursive_cfg_substitute(original_dict[key], substitution_dict)
        elif key in substitution_dict:
            # original_dict = dict(original_dict)
            original_dict[key] = substitution_dict[key]
    return original_dict


def recursive_cfg_search(original_dict: Union[dict, DictConfig], searched_key: Union[str, int]) -> Tuple[Any, bool]:
    """
    This function searches for a key in the original dictionary.
    Parameters
    ----------
    original_dict : dict
    searched_key : str

    Returns
    -------
    Tuple[Any, bool]
    """
    searched_value = None
    key_found = False

    for key in original_dict:

        if type(original_dict[key]) in (dict, DictConfig):
            searched_value, key_found = recursive_cfg_search(original_dict[key], searched_key)

        elif key == searched_key:
            searched_value = original_dict[key]
            key_found = True

        if key_found is True:  # searched_value is not None:
            break
    return searched_value, key_found


def join_dictionaries(*dicts):
    result = {}

    for d in dicts:
        for key, value in d.items():
            if key in result:
                if type(value) == pd.Series:
                    result[key] = pd.concat([result[key], value])
                elif type(value) == pd.DataFrame:
                    result[key] = pd.concat([result[key], value], axis=-1)
                elif type(value) in (dict, DictConfig):
                    result[key] = join_dictionaries(result[key], value)
                else:
                    result[key] += value
            else:
                result[key] = value

    return result


def join_preprocessing_params(*params_dicts):
    result = OmegaConf.to_object(params_dicts[0])

    for d in params_dicts[1:]:
        for key, value in d.items():
            if key not in result:
                result[key] = value
            elif type(value) == pd.Series:
                result[key] = pd.concat([result[key], value])
            elif type(value) == pd.DataFrame:
                result[key] = pd.concat([result[key], value], axis=-1)
            elif key.endswith("columns"):
                result[key] = join_columns_dicts(result[key], value)

    return result


def join_columns_dicts(*dicts):
    dict1 = dicts[0]
    if not dict1:
        max_key = 0
    else:
        max_key = max([int(key) for key in dict1.keys()]) + 1

    for d in dicts[1:]:
        for key, value in d.items():
            if key in dict1:
                dict1[max_key + key] = value
            else:
                dict1[key] = value

    return dict1


def longest_common_substring(strings):
    if not strings:
        return ""

    # Find the shortest string in the list
    shortest_string = min(strings, key=len)

    # Function to check if a substring is common to all strings
    def is_common_substring(substring):
        return all(substring in string for string in strings)

    # Iterate over all possible substrings of the shortest string
    for length in range(len(shortest_string), 0, -1):
        for start in range(len(shortest_string) - length + 1):
            substring = shortest_string[start:start + length]
            if is_common_substring(substring):
                if substring[-1] == "_":
                    substring = substring[:-1]
                return substring

    return ""


def do_nothing( *args, **_ ) -> Union[ Any, Tuple[Any]]:
    """
    This function does nothing to the positional arguments.
    Based on the 'return_first' parameter, it returns all the inputs or just the first one.

    Parameters:
        args:
            Positional arguments.

    Returns:

    """
    if len(args) == 1:
        args = args[0]
    return args


def do_really_nothing( *_, **__ ) -> None:
    """
    This function does nothing.

    Parameters:

    Returns:

    None

    """
    pass


def play_sound() -> None:  # TODO: add windows and linux sounds
    """
    This function plays a sound.

    Returns:

    None

    """
    os.system('afplay /System/Library/Sounds/Glass.aiff')


if __name__ == "__main__":
    pass
