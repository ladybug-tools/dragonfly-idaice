"""Test the CLI commands"""
import os
from click.testing import CliRunner

from dragonfly_idaice.cli.translate import model_to_idm_cli


def test_df_model_to_idm():
    runner = CliRunner()
    input_df_model = './tests/assets/simple_model.dfjson'
    output_idm = './tests/assets/simple_model.idm'

    in_args = [input_df_model, '--wall-thickness', '0', '--output-file', output_idm]
    result = runner.invoke(model_to_idm_cli, in_args)
    assert result.exit_code == 0
    assert os.path.isfile(output_idm)
    os.remove(output_idm)


def test_large_model_to_idm():
    runner = CliRunner()
    input_df_model = './tests/assets/model_for_idaice.dfjson'
    output_idm = './tests/assets/model_for_idaice.idm'

    in_args = [input_df_model, '--wall-thickness', '0.8m',
               '--adjacency-distance', '0.8m', '--output-file', output_idm]
    result = runner.invoke(model_to_idm_cli, in_args)
    assert result.exit_code == 0
    assert os.path.isfile(output_idm)
    os.remove(output_idm)
