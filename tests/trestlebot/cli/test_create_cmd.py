""" Unit test for create commands ssp and cd"""

# import pathlib

from click.testing import CliRunner

from trestlebot.cli.commands.create import create_cmd


def test_invalid_create_cmd() -> None:
    """Tests that create command fails if given invalid oscal model subcommand."""
    runner = CliRunner()
    result = runner.invoke(create_cmd, ["invalid"])

    assert "Error: No such command 'invalid'" in result.output
    assert result.exit_code == 2


# def test_create_ssp_cmd(tmp_init_dir: str) -> None:
#     """Tests successful create ssp command."""
#
#     SSP_INDEX_FILE = "test-ssp-index.json"
#
#     runner = CliRunner()
#     result = runner.invoke(
#         create_cmd,
# [
#         "ssp",
#         "--profile-name",
#         "repo-path",
#         tmp_init_dir,
#         "--ssp-index-file",
#         SSP_INDEX_FILE,
#         ],
#     )
#     assert result.exit_code == 0
#
#     # verify ssp-index.json was created in tmp_init_dir
#     tmp_dir = pathlib.Path(tmp_init_dir)
#     ssp_index_file = tmp_dir.joinpath(SSP_INDEX_FILE)
#     print("SSP INDEX Path", str(ssp_index_file.resolve()))
#
#     assert ssp_index_file.exists() is True

# verity json file was created in tmp_init_dir/system-security-plans

# verify markdown file(s) were created in tmp_init_dir/markdown/system...
