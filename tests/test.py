# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Base test classes following OpenStack/Nova patterns."""

import importlib.util
import pathlib

from oslo_config import cfg
from oslotest import base

from tests.local_fixtures.conf import ConfFixture


CONF = cfg.CONF


def load_script(script_path, module_name=None):
    """Load a standalone Python script as a module.

    This is used to import scripts from tools/ and roles/*/files/
    directories which are not Python packages (no __init__.py).

    :param script_path: Path to the .py script file (relative to repo root)
    :param module_name: Optional module name (defaults to filename stem)
    :returns: The loaded module
    """
    repo_root = pathlib.Path(__file__).parent.parent
    full_path = repo_root / script_path
    if module_name is None:
        module_name = full_path.stem
    spec = importlib.util.spec_from_file_location(module_name, full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCase(base.BaseTestCase):
    """Base test case for unit tests.

    For tests that don't need database or external services,
    use NoDBTestCase for better performance.
    """

    USES_DB = False
    REQUIRES_LOCKING = False
    STUB_RPC = False

    def setUp(self):
        super().setUp()

        # Configuration fixture for test defaults
        self.useFixture(ConfFixture(CONF))

    def flags(self, **kw):
        """Override flag variables for a test.

        Automatically registers cleanup to restore original values.

        :param kw: Keyword arguments where keys are config option names
                   and values are the values to set. Special keyword 'group'
                   specifies the config group (defaults to DEFAULT).
        """
        group = kw.pop('group', None)
        for k, v in kw.items():
            CONF.set_override(k, v, group)
            self.addCleanup(CONF.clear_override, k, group)


class NoDBTestCase(TestCase):
    """Base test case for tests that don't need external dependencies.

    This is the preferred base class for most tests in this repository
    since we don't use databases or RPC.
    """

    USES_DB = False
