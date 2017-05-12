#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os
import re

import pytest
import sh

from molecule import config
from molecule import util

pytestmark = pytest.helpers.supports_docker()


def test_command_init_role_goss(temp_dir):
    role_directory = os.path.join(temp_dir.strpath, 'test-init')
    cmd = sh.molecule.bake('init', 'role', '--role-name', 'test-init',
                           '--verifier-name', 'goss')
    pytest.helpers.run_command(cmd)

    os.chdir(role_directory)

    sh.molecule('test')


def test_command_init_scenario_goss(temp_dir):
    molecule_directory = config.molecule_directory(temp_dir.strpath)
    scenario_directory = os.path.join(molecule_directory, 'test-scenario')
    cmd = sh.molecule.bake('init', 'scenario', '--scenario-name',
                           'test-scenario', '--role-name', 'test-init',
                           '--verifier-name', 'goss')
    pytest.helpers.run_command(cmd)

    assert os.path.isdir(scenario_directory)


@pytest.mark.parametrize(
    'with_scenario', ['overrride_driver'], indirect=['with_scenario'])
def test_command_test_overrides_driver(with_scenario):
    cmd = sh.molecule.bake('test', '--driver-name', 'docker')
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'with_scenario', ['host_group_vars'], indirect=['with_scenario'])
def test_host_group_vars(with_scenario):
    cmd = sh.molecule.bake('test')
    out = pytest.helpers.run_command(cmd, log=False)
    out = util.strip_ansi_escape(out.stdout)

    assert re.search('\[all\].*?ok: \[instance-1-default\]', out, re.DOTALL)
    assert re.search('\[example\].*?ok: \[instance-1-default\]', out,
                     re.DOTALL)
    assert re.search('\[example_1\].*?ok: \[instance-1-default\]', out,
                     re.DOTALL)


@pytest.mark.parametrize(
    'with_scenario', ['interpolation'], indirect=['with_scenario'])
def test_interpolation(with_scenario):
    env = os.environ.copy()
    env.update({'DEPENDENCY_NAME': 'galaxy', 'VERIFIER_NAME': 'testinfra'})

    cmd = sh.molecule.bake('test')
    pytest.helpers.run_command(cmd, env=env)


@pytest.mark.parametrize(
    'with_scenario', ['verifier'], indirect=['with_scenario'])
def test_command_verify_testinfra(with_scenario):
    cmd = sh.molecule.bake('create', '--scenario-name', 'testinfra')
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake('converge', '--scenario-name', 'testinfra')
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake('verify', '--scenario-name', 'testinfra')
    pytest.helpers.run_command(cmd)


@pytest.mark.parametrize(
    'with_scenario', ['verifier'], indirect=['with_scenario'])
def test_command_verify_goss(with_scenario):
    cmd = sh.molecule.bake('create', '--scenario-name', 'goss')
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake('converge', '--scenario-name', 'goss')
    pytest.helpers.run_command(cmd)

    cmd = sh.molecule.bake('verify', '--scenario-name', 'goss')
    pytest.helpers.run_command(cmd)
