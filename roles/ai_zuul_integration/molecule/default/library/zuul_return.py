#!/usr/bin/python
# Copyright 2025 Sean Mooney
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Stub zuul_return module for molecule testing.

The real zuul_return module is provided by the Zuul executor environment
and is not available outside of Zuul CI. This stub allows molecule tests
to run without errors when the role includes zuul_return tasks.
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    """Run the zuul_return stub module."""
    module = AnsibleModule(
        argument_spec={
            'data': {'type': 'dict', 'required': True},
        },
        supports_check_mode=True,
    )
    module.exit_json(changed=False, msg="zuul_return stub (not in Zuul)")


if __name__ == '__main__':
    main()
