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

"""Configuration fixtures for testing."""

import fixtures
from oslo_config import cfg


CONF = cfg.CONF


class ConfFixture(fixtures.Fixture):
    """Fixture to set default configuration for tests.

    This sets up sensible defaults that can be overridden per-test
    using self.flags() or ConfPatcher.
    """

    def __init__(self, conf):
        super().__init__()
        self.conf = conf

    def setUp(self):
        super().setUp()
        self.conf.register_opts(
            [
                cfg.StrOpt(
                    'api_endpoint',
                    default='http://localhost:8080',
                    help='Test API endpoint',
                )
            ],
            group='claude',
        )


class ConfPatcher(fixtures.Fixture):
    """Fixture to patch configuration for a single test.

    Usage:
        self.useFixture(ConfPatcher(debug=True, group='DEFAULT'))
    """

    def __init__(self, **kw):
        super().__init__()
        self.kw = kw

    def setUp(self):
        super().setUp()
        group = self.kw.pop('group', None)

        # Store original values for cleanup
        self.originals = {}
        for k, v in self.kw.items():
            self.originals[k] = CONF.get(k, group=group)
            CONF.set_override(k, v, group)

        # Register cleanup
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        """Restore original configuration values."""
        group = self.kw.get('group')
        for k, v in self.originals.items():
            if v is None:
                CONF.clear_override(k, group)
            else:
                CONF.set_override(k, v, group)
