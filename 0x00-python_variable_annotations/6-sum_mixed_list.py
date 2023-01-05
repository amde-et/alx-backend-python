#!/usr/bin/env python3
"""
Contains a function that takes a mixed list of integers and
floats and returns the sum of all the numbers in the list as float
"""
from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[int, float]]) -> float:
    """Takes a mixed list of integers and floats and returns the
    sum of all the numbers in the list as float"""
    return sum(mxd_lst)
