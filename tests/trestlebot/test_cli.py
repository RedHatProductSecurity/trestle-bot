#!/usr/bin/python

#    Copyright 2023 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Test for CLI"""

import logging
import sys
from typing import List

import pytest

from trestlebot.cli import run as cli_main


@pytest.fixture
def valid_args_dict() -> dict:
    return {
        "branch": "main",
        "markdown-path": "/my/path",
        "assemble-model": "profile",
        "committer-name": "test",
        "committer-email": "test@email.com",
        "working-dir": "tmp",
        "patterns": ".",
    }


def args_dict_to_list(args_dict: dict) -> List[str]:
    args = []
    for k, v in args_dict.items():
        args.append(f"--{k}")
        if v is not None:
            args.append(v)
    return args


def test_invalid_assemble_model(monkeypatch, valid_args_dict, caplog):
    """Test invalid assemble model"""
    args_dict = valid_args_dict
    args_dict["assemble-model"] = "fake"
    monkeypatch.setattr(sys, "argv", ["trestlebot", *args_dict_to_list(args_dict)])

    with pytest.raises(SystemExit):
        cli_main()

    assert any(
        record.levelno == logging.ERROR
        and record.message
        == "Invalid value fake for assemble model. Please use catalog, profile, compdef, or ssp."
        for record in caplog.records
    )


def test_no_ssp_index(monkeypatch, valid_args_dict, caplog):
    """Test invalid assemble model"""
    args_dict = valid_args_dict
    args_dict["assemble-model"] = "ssp"
    args_dict["ssp-index-path"] = ""
    monkeypatch.setattr(sys, "argv", ["trestlebot", *args_dict_to_list(args_dict)])

    with pytest.raises(SystemExit):
        cli_main()

    assert any(
        record.levelno == logging.ERROR
        and record.message
        == "Must set ssp_index_path when using SSP as assemble model."
        for record in caplog.records
    )
