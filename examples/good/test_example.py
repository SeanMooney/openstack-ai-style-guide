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

"""Test cases demonstrating proper OpenStack testing patterns."""

from unittest import mock

from oslo_config import cfg
from oslo_utils import uuidutils

from nova import exception
from nova import test
from nova.tests.unit import fake_instance

CONF = cfg.CONF


class TestResourceManager(test.NoDBTestCase):
    """Test cases for ResourceManager class."""

    def setUp(self):
        super().setUp()
        self.manager = self._get_manager()

    def _get_manager(self):
        """Create a ResourceManager instance for testing."""
        from examples.good.basic_service import ResourceManager
        return ResourceManager(timeout=30)

    @mock.patch('examples.good.basic_service.time.time', autospec=True)
    def test_create_resource_success(self, mock_time):
        """Test successful resource creation."""
        mock_time.return_value = 1234567890
        resource_uuid = uuidutils.generate_uuid()
        
        with mock.patch.object(self.manager, '_create_in_db',
                              autospec=True) as mock_create:
            mock_resource = mock.Mock()
            mock_resource.id = resource_uuid
            mock_create.return_value = mock_resource
            
            with mock.patch.object(self.manager, '_get_db_session',
                                  autospec=True) as mock_session:
                mock_session.return_value.__enter__.return_value = mock.Mock()
                
                result = self.manager.create_resource('test-resource')
                
                self.assertEqual(resource_uuid, result.id)
                mock_create.assert_called_once()

    def test_create_resource_empty_name(self):
        """Test resource creation with empty name raises ValueError."""
        self.assertRaises(ValueError,
                         self.manager.create_resource, '')

    def test_create_resource_none_name(self):
        """Test resource creation with None name raises ValueError."""
        self.assertRaises(ValueError,
                         self.manager.create_resource, None)

    @mock.patch('examples.good.basic_service.LOG', autospec=True)
    def test_create_resource_duplicate(self, mock_log):
        """Test resource creation handles duplicate resources properly."""
        with mock.patch.object(self.manager, '_create_in_db',
                              autospec=True) as mock_create:
            mock_create.side_effect = exception.Duplicate()
            
            with mock.patch.object(self.manager, '_get_db_session',
                                  autospec=True) as mock_session:
                mock_session.return_value.__enter__.return_value = mock.Mock()
                
                self.assertRaises(exception.ResourceExists,
                                self.manager.create_resource, 'duplicate')
                
                mock_log.warning.assert_called_once()

    def test_get_resource_empty_id(self):
        """Test get_resource with empty ID raises ValueError."""
        self.assertRaises(ValueError,
                         self.manager.get_resource, '')

    @mock.patch('examples.good.basic_service.LOG', autospec=True)
    def test_get_resource_invalid_format(self, mock_log):
        """Test get_resource handles invalid ID format."""
        with mock.patch.object(self.manager, '_fetch_from_db',
                              autospec=True) as mock_fetch:
            mock_fetch.side_effect = ValueError('Invalid UUID format')
            
            self.assertRaises(exception.InvalidInput,
                             self.manager.get_resource, 'invalid-id')
            
            mock_log.error.assert_called_once_with(
                'Invalid resource ID format: %s', mock.ANY)

    def test_get_resource_not_found(self):
        """Test get_resource raises ResourceNotFound for missing resource."""
        resource_id = uuidutils.generate_uuid()
        
        with mock.patch.object(self.manager, '_fetch_from_db',
                              autospec=True) as mock_fetch:
            mock_fetch.return_value = None
            
            self.assertRaises(exception.ResourceNotFound,
                             self.manager.get_resource, resource_id)

    def test_create_resource_with_properties(self):
        """Test resource creation with custom properties."""
        properties = {'flavor': 'm1.small', 'image': 'ubuntu-20.04'}
        
        with mock.patch.object(self.manager, '_create_in_db',
                              autospec=True) as mock_create:
            mock_resource = mock.Mock()
            mock_create.return_value = mock_resource
            
            with mock.patch.object(self.manager, '_get_db_session',
                                  autospec=True) as mock_session:
                mock_session.return_value.__enter__.return_value = mock.Mock()
                
                self.manager.create_resource('test-resource', properties)
                
                # Verify properties were passed correctly
                call_args = mock_create.call_args[0][1]
                self.assertEqual(properties, call_args['properties'])