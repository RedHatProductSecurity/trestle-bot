# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 Red Hat, Inc.


"""
Trestle custom validation error messages with pydantic.
"""

from typing import Any, Dict, List, Tuple, Union

from pydantic import ValidationError


# From https://docs.pydantic.dev/latest/errors/errors/


def loc_to_dot_sep(loc: Tuple[Union[str, int], ...]) -> str:
    """Convert a tuple of strings and integers to a dot separated string."""
    path = ""
    for i, x in enumerate(loc):
        if isinstance(x, str):
            if i > 0:
                path += "."
            path += x
        elif isinstance(x, int):
            path += f"[{x}]"
        else:
            raise TypeError("Unexpected type")
    return path


def convert_errors(e: ValidationError) -> List[Dict[str, Any]]:
    """
    Convert pydantic validation errors to a list of dictionaries.

    Note: All validations for rules should be done in the pydantic model and
    formatted through this function.
    """
    new_errors: List[Dict[str, Any]] = e.errors()
    for error in new_errors:
        error["loc"] = loc_to_dot_sep(error["loc"])
    return new_errors
