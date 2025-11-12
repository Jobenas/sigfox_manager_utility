from unittest.mock import patch, MagicMock
import pytest
from sigfox_manager.sigfox_manager import SigfoxManager
from sigfox_manager.models.schemas import ContractsResponse, DevicesResponse, DeviceTypesResponse, DeviceType, Paging
from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceTypeNotFoundException


class TestSigfoxManager:
    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_contracts(self, mock_get):
        # Mock the API response with minimal required fields
        mock_get.return_value = MagicMock(
            status_code=200, 
            text='{"data": [{"id": "1", "name": "Contract 1", "activationEndTime": 0, "communicationEndTime": 0, "bidir": false, "highPriorityDownlink": false, "maxUplinkFrames": 0, "maxDownlinkFrames": 0, "maxTokens": 0, "automaticRenewal": false, "renewalDuration": 0, "contractId": "c1", "userId": "u1", "createdBy": "user", "lastEditionTime": 0, "creationTime": 0, "lastEditedBy": "user", "startTime": 0, "timezone": "UTC", "tokenDuration": 0, "tokensInUse": 0, "tokensUsed": 0}], "paging": {"next": null}}'
        )

        # Initialize SigfoxManager
        sm = SigfoxManager("user", "pwd")

        # Call the method
        response = sm.get_contracts()

        # Assert the response
        assert isinstance(response, ContractsResponse)
        assert response.data[0].id == "1"
        assert response.data[0].name == "Contract 1"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_devices_by_contract(self, mock_get):
        # Mock the API response with minimal required fields
        mock_get.return_value = MagicMock(
            status_code=200, 
            text='{"data": [{"id": "1", "name": "Device 1", "satelliteCapable": false, "repeater": false, "messageModulo": 0, "group": {"id": "g1"}, "prototype": false, "location": {"lat": 0.0, "lng": 0.0}, "pac": "0000000000000000", "lqi": 0, "creationTime": 0, "state": 0, "comState": 0, "createdBy": "user", "lastEditionTime": 0, "lastEditedBy": "user", "automaticRenewal": false, "automaticRenewalStatus": 0, "activable": false}], "paging": {"next": null}}'
        )

        # Initialize SigfoxManager
        sm = SigfoxManager("user", "pwd")

        # Call the method
        response = sm.get_devices_by_contract("1")

        # Assert the response
        assert isinstance(response, DevicesResponse)
        assert response.data[0].id == "1"
        assert response.data[0].name == "Device 1"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_paginates_and_merges(self, mock_get):
        """Test that get_device_types fetches all pages and merges data"""
        # Mock two pages of device types
        page1_response = MagicMock(
            status_code=200,
            text='{"data": [{"id": "dt1", "name": "Type A"}], "paging": {"next": "https://api.sigfox.com/v2/devicetypes?page=2"}}'
        )
        page2_response = MagicMock(
            status_code=200,
            text='{"data": [{"id": "dt2", "name": "Type B"}], "paging": {"next": null}}'
        )
        
        # Configure mock to return different responses for each call
        mock_get.side_effect = [page1_response, page2_response]
        
        # Initialize SigfoxManager
        sm = SigfoxManager("user", "pwd")
        
        # Call the method with fetch_all_pages=True
        response = sm.get_device_types(fetch_all_pages=True)
        
        # Assert the response contains both items
        assert isinstance(response, DeviceTypesResponse)
        assert len(response.data) == 2
        assert response.data[0].id == "dt1"
        assert response.data[0].name == "Type A"
        assert response.data[1].id == "dt2"
        assert response.data[1].name == "Type B"
        assert response.paging.next is None
        
        # Verify do_get was called twice
        assert mock_get.call_count == 2

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_single_page(self, mock_get):
        """Test that get_device_types returns single page when fetch_all_pages=False"""
        # Mock single page response
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"data": [{"id": "dt1", "name": "Type A"}], "paging": {"next": "https://api.sigfox.com/v2/devicetypes?page=2"}}'
        )
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_device_types(fetch_all_pages=False)
        
        assert isinstance(response, DeviceTypesResponse)
        assert len(response.data) == 1
        assert response.paging.next is not None
        assert mock_get.call_count == 1

    @patch.object(SigfoxManager, "get_device_types")
    def test_resolve_device_type_id_by_id(self, mock_get_device_types):
        """Test resolving device type by id"""
        # Use real Pydantic objects
        dt1 = DeviceType(id="dt1", name="Type A")
        dt2 = DeviceType(id="dt2", name="Type B")
        
        mock_response = DeviceTypesResponse(
            data=[dt1, dt2],
            paging=Paging(next=None)
        )
        mock_get_device_types.return_value = mock_response
        
        sm = SigfoxManager("user", "pwd")
        result = sm.resolve_device_type_id("dt1")
        
        assert result == "dt1"
        mock_get_device_types.assert_called_once_with(fetch_all_pages=True)

    @patch.object(SigfoxManager, "get_device_types")
    def test_resolve_device_type_id_by_name(self, mock_get_device_types):
        """Test resolving device type by name"""
        # Use real Pydantic objects instead of MagicMock for proper equality checks
        dt1 = DeviceType(id="dt1", name="Type A")
        dt2 = DeviceType(id="dt2", name="Type B")
        
        mock_response = DeviceTypesResponse(
            data=[dt1, dt2],
            paging=Paging(next=None)
        )
        mock_get_device_types.return_value = mock_response
        
        sm = SigfoxManager("user", "pwd")
        result = sm.resolve_device_type_id("Type A")
        
        assert result == "dt1"
        mock_get_device_types.assert_called_once_with(fetch_all_pages=True)

    @patch.object(SigfoxManager, "get_device_types")
    def test_resolve_device_type_id_not_found(self, mock_get_device_types):
        """Test that resolve_device_type_id raises exception when not found"""
        # Use real Pydantic objects
        dt1 = DeviceType(id="dt1", name="Type A")
        dt2 = DeviceType(id="dt2", name="Type B")
        
        mock_response = DeviceTypesResponse(
            data=[dt1, dt2],
            paging=Paging(next=None)
        )
        mock_get_device_types.return_value = mock_response
        
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceTypeNotFoundException) as exc_info:
            sm.resolve_device_type_id("NonExistent")
        
        assert "Device type not found: NonExistent" in str(exc_info.value)

    @patch.object(SigfoxManager, "create_device")
    @patch.object(SigfoxManager, "resolve_device_type_id")
    def test_provision_device_validates_and_calls_create(self, mock_resolve, mock_create):
        """Test provision_device validates inputs and calls create_device"""
        # Mock resolve_device_type_id to return a device type id
        mock_resolve.return_value = "dt1"
        
        # Mock create_device to return a BaseDevice
        mock_device = MagicMock(id="19C3B", name="field-node-42")
        mock_create.return_value = mock_device
        
        sm = SigfoxManager("user", "pwd")
        
        # Call provision_device with valid inputs
        result = sm.provision_device(
            dev_id="19C3B",
            pac="1234567890ABCDEF",
            dev_type_ref="Type A",
            name="field-node-42",
            automatic_renewal=True
        )
        
        # Verify resolve_device_type_id was called
        mock_resolve.assert_called_once_with("Type A")
        
        # Verify create_device was called with correct parameters
        mock_create.assert_called_once_with(
            dev_id="19C3B",
            pac="1234567890ABCDEF",
            dev_type_id="dt1",
            name="field-node-42",
            activable=True,
            lat=0.0,
            lng=0.0,
            product_cert=None,
            prototype=False,
            automatic_renewal=True
        )
        
        assert result == mock_device

    def test_provision_device_invalid_dev_id(self):
        """Test provision_device raises ValueError for invalid dev_id"""
        sm = SigfoxManager("user", "pwd")
        
        # Test lowercase
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="19c3b",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )
        assert "Invalid dev_id format" in str(exc_info.value)
        
        # Test too short
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="AB",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )
        assert "Invalid dev_id format" in str(exc_info.value)
        
        # Test too long
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="12345678901234567",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )
        assert "Invalid dev_id format" in str(exc_info.value)
        
        # Test non-hex characters
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="ZZZZZ",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )
        assert "Invalid dev_id format" in str(exc_info.value)

    def test_provision_device_invalid_pac(self):
        """Test provision_device raises ValueError for invalid pac"""
        sm = SigfoxManager("user", "pwd")
        
        # Test too short
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="19C3B",
                pac="123456789",
                dev_type_ref="Type A"
            )
        assert "Invalid pac format" in str(exc_info.value)
        
        # Test too long
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="19C3B",
                pac="1234567890ABCDEF123",
                dev_type_ref="Type A"
            )
        assert "Invalid pac format" in str(exc_info.value)
        
        # Test special characters
        with pytest.raises(ValueError) as exc_info:
            sm.provision_device(
                dev_id="19C3B",
                pac="123456789@ABCDEF",
                dev_type_ref="Type A"
            )
        assert "Invalid pac format" in str(exc_info.value)

    @patch.object(SigfoxManager, "create_device")
    @patch.object(SigfoxManager, "resolve_device_type_id")
    def test_provision_device_uses_dev_id_as_default_name(self, mock_resolve, mock_create):
        """Test provision_device uses dev_id as name when name not provided"""
        mock_resolve.return_value = "dt1"
        mock_device = MagicMock(id="ABC123")
        mock_create.return_value = mock_device
        
        sm = SigfoxManager("user", "pwd")
        sm.provision_device(
            dev_id="ABC123",
            pac="1234567890ABCDEF",
            dev_type_ref="Type A"
        )
        
        # Verify create_device was called with dev_id as name
        call_args = mock_create.call_args
        assert call_args[1]['name'] == "ABC123"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_handles_403_auth_error(self, mock_get):
        """Test that get_device_types raises SigfoxAuthError on 403"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAuthError
        
        mock_get.return_value = MagicMock(status_code=403)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAuthError):
            sm.get_device_types()

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_handles_non_200_error(self, mock_get):
        """Test that get_device_types raises SigfoxAPIException on non-200 status"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAPIException
        
        mock_get.return_value = MagicMock(status_code=500, text="Internal Server Error")
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAPIException) as exc_info:
            sm.get_device_types()
        
        assert exc_info.value.status_code == 500

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_handles_pagination_error(self, mock_get):
        """Test get_device_types handles errors in pagination gracefully"""
        # First page succeeds, second page fails
        page1_response = MagicMock(
            status_code=200,
            text='{"data": [{"id": "dt1", "name": "Type A"}], "paging": {"next": "https://api.sigfox.com/v2/devicetypes?page=2"}}'
        )
        page2_response = MagicMock(status_code=500)
        
        mock_get.side_effect = [page1_response, page2_response]
        sm = SigfoxManager("user", "pwd")
        
        # Should return what we got before the error
        response = sm.get_device_types(fetch_all_pages=True)
        
        assert len(response.data) == 1
        assert response.data[0].id == "dt1"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_no_pagination(self, mock_get):
        """Test get_device_types with no pagination in response"""
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"data": [{"id": "dt1", "name": "Type A"}], "paging": {"next": null}}'
        )
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_device_types(fetch_all_pages=True)
        
        assert len(response.data) == 1
        assert response.paging.next is None
        assert mock_get.call_count == 1

    @patch.object(SigfoxManager, "get_device_types")
    def test_resolve_device_type_id_with_none_values(self, mock_get_device_types):
        """Test resolve_device_type_id handles device types with None id or name"""
        # Some device types might have None for id or name
        dt1 = DeviceType(id=None, name="Type A")
        dt2 = DeviceType(id="dt2", name=None)
        dt3 = DeviceType(id="dt3", name="Type C")
        
        mock_response = DeviceTypesResponse(
            data=[dt1, dt2, dt3],
            paging=Paging(next=None)
        )
        mock_get_device_types.return_value = mock_response
        
        sm = SigfoxManager("user", "pwd")
        
        # Should find dt3
        result = sm.resolve_device_type_id("dt3")
        assert result == "dt3"
        
        # Should find by name even if previous entries have None
        result = sm.resolve_device_type_id("Type C")
        assert result == "dt3"

    @patch.object(SigfoxManager, "resolve_device_type_id")
    def test_provision_device_propagates_resolve_exception(self, mock_resolve):
        """Test provision_device propagates SigfoxDeviceTypeNotFoundException"""
        mock_resolve.side_effect = SigfoxDeviceTypeNotFoundException("Not found")
        
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceTypeNotFoundException):
            sm.provision_device(
                dev_id="ABC123",
                pac="1234567890ABCDEF",
                dev_type_ref="NonExistent"
            )

    @patch.object(SigfoxManager, "create_device")
    @patch.object(SigfoxManager, "resolve_device_type_id")
    def test_provision_device_with_all_kwargs(self, mock_resolve, mock_create):
        """Test provision_device passes through all optional kwargs"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceCreateConflictException
        
        mock_resolve.return_value = "dt1"
        mock_device = MagicMock(id="ABC123")
        mock_create.return_value = mock_device
        
        sm = SigfoxManager("user", "pwd")
        sm.provision_device(
            dev_id="ABC123",
            pac="1234567890ABCDEF",
            dev_type_ref="Type A",
            name="custom-name",
            prototype=True,
            automatic_renewal=False,
            lat=45.5,
            lng=-73.6,
            activable=False,
            product_cert={"key": "test"}
        )
        
        # Verify all parameters were passed
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs['name'] == "custom-name"
        assert call_kwargs['prototype'] is True
        assert call_kwargs['automatic_renewal'] is False
        assert call_kwargs['lat'] == 45.5
        assert call_kwargs['lng'] == -73.6
        assert call_kwargs['activable'] is False
        assert call_kwargs['product_cert'] == {"key": "test"}

    @patch.object(SigfoxManager, "create_device")
    @patch.object(SigfoxManager, "resolve_device_type_id")
    def test_provision_device_propagates_create_exceptions(self, mock_resolve, mock_create):
        """Test provision_device propagates exceptions from create_device"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceCreateConflictException
        
        mock_resolve.return_value = "dt1"
        mock_create.side_effect = SigfoxDeviceCreateConflictException()
        
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceCreateConflictException):
            sm.provision_device(
                dev_id="ABC123",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )

    def test_provision_device_edge_case_dev_id_length(self):
        """Test provision_device accepts edge case lengths for dev_id"""
        sm = SigfoxManager("user", "pwd")
        
        # Test minimum valid length (3 chars)
        with patch.object(SigfoxManager, "resolve_device_type_id") as mock_resolve, \
             patch.object(SigfoxManager, "create_device") as mock_create:
            mock_resolve.return_value = "dt1"
            mock_create.return_value = MagicMock(id="ABC")
            
            result = sm.provision_device(
                dev_id="ABC",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )
            assert result is not None
        
        # Test maximum valid length (16 chars)
        with patch.object(SigfoxManager, "resolve_device_type_id") as mock_resolve, \
             patch.object(SigfoxManager, "create_device") as mock_create:
            mock_resolve.return_value = "dt1"
            mock_create.return_value = MagicMock(id="1234567890ABCDEF")
            
            result = sm.provision_device(
                dev_id="1234567890ABCDEF",
                pac="1234567890ABCDEF",
                dev_type_ref="Type A"
            )
            assert result is not None

    def test_provision_device_valid_pac_formats(self):
        """Test provision_device accepts various valid PAC formats"""
        sm = SigfoxManager("user", "pwd")
        
        valid_pacs = [
            "1234567890ABCDEF",  # uppercase hex
            "1234567890abcdef",  # lowercase hex
            "1234567890AbCdEf",  # mixed case
            "0000000000000000",  # all zeros
            "FFFFFFFFFFFFFFFF",  # all F
        ]
        
        for pac in valid_pacs:
            with patch.object(SigfoxManager, "resolve_device_type_id") as mock_resolve, \
                 patch.object(SigfoxManager, "create_device") as mock_create:
                mock_resolve.return_value = "dt1"
                mock_create.return_value = MagicMock(id="ABC123")
                
                result = sm.provision_device(
                    dev_id="ABC123",
                    pac=pac,
                    dev_type_ref="Type A"
                )
                assert result is not None

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_empty_response(self, mock_get):
        """Test get_device_types handles empty device type list"""
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"data": [], "paging": {"next": null}}'
        )
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_device_types()
        
        assert isinstance(response, DeviceTypesResponse)
        assert len(response.data) == 0
        assert response.paging.next is None

    @patch.object(SigfoxManager, "get_device_types")
    def test_resolve_device_type_id_empty_list(self, mock_get_device_types):
        """Test resolve_device_type_id raises exception with empty device type list"""
        mock_response = DeviceTypesResponse(
            data=[],
            paging=Paging(next=None)
        )
        mock_get_device_types.return_value = mock_response
        
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceTypeNotFoundException):
            sm.resolve_device_type_id("AnyType")

    # Tests for existing methods not yet covered
    
    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_contracts_pagination_merges_multiple_pages(self, mock_get):
        """Test get_contracts with multiple pages of contracts"""
        page1 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "c1", "name": "Contract 1", "activationEndTime": 0, "communicationEndTime": 0, "bidir": false, "highPriorityDownlink": false, "maxUplinkFrames": 0, "maxDownlinkFrames": 0, "maxTokens": 0, "automaticRenewal": false, "renewalDuration": 0, "contractId": "c1", "userId": "u1", "createdBy": "user", "lastEditionTime": 0, "creationTime": 0, "lastEditedBy": "user", "startTime": 0, "timezone": "UTC", "tokenDuration": 0, "tokensInUse": 0, "tokensUsed": 0}], "paging": {"next": "https://api.sigfox.com/v2/contract-infos?page=2"}}'
        )
        page2 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "c2", "name": "Contract 2", "activationEndTime": 0, "communicationEndTime": 0, "bidir": false, "highPriorityDownlink": false, "maxUplinkFrames": 0, "maxDownlinkFrames": 0, "maxTokens": 0, "automaticRenewal": false, "renewalDuration": 0, "contractId": "c2", "userId": "u1", "createdBy": "user", "lastEditionTime": 0, "creationTime": 0, "lastEditedBy": "user", "startTime": 0, "timezone": "UTC", "tokenDuration": 0, "tokensInUse": 0, "tokensUsed": 0}], "paging": {"next": null}}'
        )
        mock_get.side_effect = [page1, page2]
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_contracts(fetch_all_pages=True)
        
        assert len(response.data) == 2
        assert response.data[0].id == "c1"
        assert response.data[1].id == "c2"
        assert response.paging.next is None
        assert mock_get.call_count == 2

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_contracts_error_handling(self, mock_get):
        """Test get_contracts raises SigfoxAPIException on non-200"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAPIException
        
        mock_get.return_value = MagicMock(status_code=500)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAPIException) as exc_info:
            sm.get_contracts()
        
        assert exc_info.value.status_code == 500

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_devices_by_contract_pagination(self, mock_get):
        """Test get_devices_by_contract with pagination"""
        page1 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "d1", "name": "Device 1", "satelliteCapable": false, "repeater": false, "messageModulo": 0, "group": {"id": "g1"}, "prototype": false, "location": {"lat": 0.0, "lng": 0.0}, "pac": "0000000000000000", "lqi": 0, "creationTime": 0, "state": 0, "comState": 0, "createdBy": "user", "lastEditionTime": 0, "lastEditedBy": "user", "automaticRenewal": false, "automaticRenewalStatus": 0, "activable": false}], "paging": {"next": "https://api.sigfox.com/v2/devices?page=2"}}'
        )
        page2 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "d2", "name": "Device 2", "satelliteCapable": false, "repeater": false, "messageModulo": 0, "group": {"id": "g1"}, "prototype": false, "location": {"lat": 0.0, "lng": 0.0}, "pac": "0000000000000000", "lqi": 0, "creationTime": 0, "state": 0, "comState": 0, "createdBy": "user", "lastEditionTime": 0, "lastEditedBy": "user", "automaticRenewal": false, "automaticRenewalStatus": 0, "activable": false}], "paging": {"next": null}}'
        )
        mock_get.side_effect = [page1, page2]
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_devices_by_contract("c1", fetch_all_pages=True)
        
        assert len(response.data) == 2
        assert response.data[0].id == "d1"
        assert response.data[1].id == "d2"
        assert mock_get.call_count == 2

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_devices_by_contract_error(self, mock_get):
        """Test get_devices_by_contract raises SigfoxDeviceNotFoundError"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceNotFoundError
        
        mock_get.return_value = MagicMock(status_code=404)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceNotFoundError):
            sm.get_devices_by_contract("nonexistent")

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_info_success(self, mock_get):
        """Test get_device_info returns device details"""
        from sigfox_manager.models.schemas import Device
        
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"id": "d1", "name": "Device 1", "satelliteCapable": false, "repeater": false, "messageModulo": 0, "group": {"id": "g1"}, "prototype": false, "location": {"lat": 0.0, "lng": 0.0}, "pac": "0000000000000000", "lqi": 0, "creationTime": 0, "state": 0, "comState": 0, "createdBy": "user", "lastEditionTime": 0, "lastEditedBy": "user", "automaticRenewal": false, "automaticRenewalStatus": 0, "activable": false}'
        )
        
        sm = SigfoxManager("user", "pwd")
        device = sm.get_device_info("d1")
        
        assert isinstance(device, Device)
        assert device.id == "d1"
        assert device.name == "Device 1"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_info_403_error(self, mock_get):
        """Test get_device_info raises SigfoxAuthError on 403"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAuthError
        
        mock_get.return_value = MagicMock(status_code=403)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAuthError):
            sm.get_device_info("d1")

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_info_404_error(self, mock_get):
        """Test get_device_info raises SigfoxDeviceNotFoundError on 404"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceNotFoundError
        
        mock_get.return_value = MagicMock(status_code=404)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceNotFoundError):
            sm.get_device_info("d1")

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_messages_without_threshold(self, mock_get):
        """Test get_device_messages retrieves all messages"""
        from sigfox_manager.models.schemas import DeviceMessagesResponse
        
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"data": [{"time": 1234567890, "data": "abc123", "lqi": 4, "seqNumber": 1, "nbFrames": 1, "computedLocation": [], "rinfos": []}], "paging": {"next": null}}'
        )
        
        sm = SigfoxManager("user", "pwd")
        messages = sm.get_device_messages("d1")
        
        assert isinstance(messages, DeviceMessagesResponse)
        assert len(messages.data) == 1

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_messages_with_threshold(self, mock_get):
        """Test get_device_messages with threshold parameter"""
        from sigfox_manager.models.schemas import DeviceMessagesResponse
        
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"data": [], "paging": {"next": null}}'
        )
        
        sm = SigfoxManager("user", "pwd")
        messages = sm.get_device_messages("d1", threshold=1234567890)
        
        assert isinstance(messages, DeviceMessagesResponse)
        # Verify the URL includes the threshold
        call_args = mock_get.call_args[0][0]
        assert "since=1234567890" in call_args

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_messages_403_error(self, mock_get):
        """Test get_device_messages raises SigfoxAuthError on 403"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAuthError
        
        mock_get.return_value = MagicMock(status_code=403)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAuthError):
            sm.get_device_messages("d1")

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_messages_404_error(self, mock_get):
        """Test get_device_messages raises SigfoxDeviceNotFoundError on 404"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceNotFoundError
        
        mock_get.return_value = MagicMock(status_code=404)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceNotFoundError):
            sm.get_device_messages("d1")

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_message_number_success(self, mock_get):
        """Test get_device_message_number returns message stats"""
        from sigfox_manager.models.schemas import DeviceMessageStats
        
        mock_get.return_value = MagicMock(
            status_code=200,
            text='{"lastDay": 10, "lastWeek": 50, "lastMonth": 200}'
        )
        
        sm = SigfoxManager("user", "pwd")
        stats = sm.get_device_message_number("d1")
        
        assert isinstance(stats, DeviceMessageStats)
        assert stats.lastDay == 10
        assert stats.lastWeek == 50
        assert stats.lastMonth == 200

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_message_number_403_error(self, mock_get):
        """Test get_device_message_number raises SigfoxAuthError on 403"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAuthError
        
        mock_get.return_value = MagicMock(status_code=403)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAuthError):
            sm.get_device_message_number("d1")

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_message_number_404_error(self, mock_get):
        """Test get_device_message_number raises SigfoxDeviceNotFoundError on 404"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceNotFoundError
        
        mock_get.return_value = MagicMock(status_code=404)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceNotFoundError):
            sm.get_device_message_number("d1")

    @patch("sigfox_manager.sigfox_manager.do_post")
    def test_create_device_success(self, mock_post):
        """Test create_device creates a device successfully"""
        from sigfox_manager.models.schemas import BaseDevice
        
        mock_post.return_value = MagicMock(
            status_code=201,
            text='{"id": "ABC123"}'
        )
        
        sm = SigfoxManager("user", "pwd")
        device = sm.create_device(
            dev_id="ABC123",
            pac="1234567890ABCDEF",
            dev_type_id="dt1",
            name="Test Device"
        )
        
        assert isinstance(device, BaseDevice)
        assert device.id == "ABC123"

    @patch("sigfox_manager.sigfox_manager.do_post")
    def test_create_device_with_product_cert(self, mock_post):
        """Test create_device with product certificate"""
        from sigfox_manager.models.schemas import BaseDevice
        
        mock_post.return_value = MagicMock(
            status_code=201,
            text='{"id": "ABC123"}'
        )
        
        sm = SigfoxManager("user", "pwd")
        product_cert = {"key": "test_cert_key"}
        device = sm.create_device(
            dev_id="ABC123",
            pac="1234567890ABCDEF",
            dev_type_id="dt1",
            name="Test Device",
            product_cert=product_cert
        )
        
        # Verify product_cert was included in the payload
        call_args = mock_post.call_args[0][1]
        assert "productCertificate" in call_args
        assert call_args["productCertificate"]["key"] == "test_cert_key"

    @patch("sigfox_manager.sigfox_manager.do_post")
    def test_create_device_with_all_parameters(self, mock_post):
        """Test create_device with all optional parameters"""
        from sigfox_manager.models.schemas import BaseDevice
        
        mock_post.return_value = MagicMock(
            status_code=201,
            text='{"id": "ABC123"}'
        )
        
        sm = SigfoxManager("user", "pwd")
        device = sm.create_device(
            dev_id="ABC123",
            pac="1234567890ABCDEF",
            dev_type_id="dt1",
            name="Test Device",
            activable=False,
            lat=45.5,
            lng=-73.6,
            prototype=True,
            automatic_renewal=False
        )
        
        # Verify all parameters were included
        call_args = mock_post.call_args[0][1]
        assert call_args["activable"] is False
        assert call_args["lat"] == 45.5
        assert call_args["lng"] == -73.6
        assert call_args["prototype"] is True
        assert call_args["automatic_renewal"] is False

    @patch("sigfox_manager.sigfox_manager.do_post")
    def test_create_device_403_error(self, mock_post):
        """Test create_device raises SigfoxAuthError on 403"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAuthError
        
        mock_post.return_value = MagicMock(status_code=403)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAuthError):
            sm.create_device(
                dev_id="ABC123",
                pac="1234567890ABCDEF",
                dev_type_id="dt1",
                name="Test Device"
            )

    @patch("sigfox_manager.sigfox_manager.do_post")
    def test_create_device_409_conflict(self, mock_post):
        """Test create_device raises SigfoxDeviceCreateConflictException on 409"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxDeviceCreateConflictException
        
        mock_post.return_value = MagicMock(status_code=409)
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxDeviceCreateConflictException):
            sm.create_device(
                dev_id="ABC123",
                pac="1234567890ABCDEF",
                dev_type_id="dt1",
                name="Test Device"
            )

    @patch("sigfox_manager.sigfox_manager.do_post")
    def test_create_device_invalid_product_cert(self, mock_post):
        """Test create_device ignores product_cert without key"""
        from sigfox_manager.models.schemas import BaseDevice
        
        mock_post.return_value = MagicMock(
            status_code=201,
            text='{"id": "ABC123"}'
        )
        
        sm = SigfoxManager("user", "pwd")
        # Product cert without 'key' should be ignored
        device = sm.create_device(
            dev_id="ABC123",
            pac="1234567890ABCDEF",
            dev_type_id="dt1",
            name="Test Device",
            product_cert={"invalid": "cert"}
        )
        
        # Verify product_cert was NOT included
        call_args = mock_post.call_args[0][1]
        assert "productCertificate" not in call_args

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_contracts_pagination_break_on_error(self, mock_get):
        """Test get_contracts breaks pagination loop on non-200 status"""
        page1 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "c1", "name": "Contract 1", "activationEndTime": 0, "communicationEndTime": 0, "bidir": false, "highPriorityDownlink": false, "maxUplinkFrames": 0, "maxDownlinkFrames": 0, "maxTokens": 0, "automaticRenewal": false, "renewalDuration": 0, "contractId": "c1", "userId": "u1", "createdBy": "user", "lastEditionTime": 0, "creationTime": 0, "lastEditedBy": "user", "startTime": 0, "timezone": "UTC", "tokenDuration": 0, "tokensInUse": 0, "tokensUsed": 0}], "paging": {"next": "https://api.sigfox.com/v2/contract-infos?page=2"}}'
        )
        page2_error = MagicMock(status_code=500)
        
        mock_get.side_effect = [page1, page2_error]
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_contracts(fetch_all_pages=True)
        
        # Should return only the first page data
        assert len(response.data) == 1
        assert response.data[0].id == "c1"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_devices_by_contract_pagination_break_on_error(self, mock_get):
        """Test get_devices_by_contract breaks pagination loop on non-200 status"""
        page1 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "d1", "name": "Device 1", "satelliteCapable": false, "repeater": false, "messageModulo": 0, "group": {"id": "g1"}, "prototype": false, "location": {"lat": 0.0, "lng": 0.0}, "pac": "0000000000000000", "lqi": 0, "creationTime": 0, "state": 0, "comState": 0, "createdBy": "user", "lastEditionTime": 0, "lastEditedBy": "user", "automaticRenewal": false, "automaticRenewalStatus": 0, "activable": false}], "paging": {"next": "https://api.sigfox.com/v2/devices?page=2"}}'
        )
        page2_error = MagicMock(status_code=500)
        
        mock_get.side_effect = [page1, page2_error]
        
        sm = SigfoxManager("user", "pwd")
        response = sm.get_devices_by_contract("c1", fetch_all_pages=True)
        
        # Should return only the first page data
        assert len(response.data) == 1
        assert response.data[0].id == "d1"

    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_device_types_pagination_break_on_403_second_page(self, mock_get):
        """Test get_device_types raises SigfoxAuthError on 403 during pagination"""
        from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import SigfoxAuthError
        
        page1 = MagicMock(
            status_code=200,
            text='{"data": [{"id": "dt1", "name": "Type A"}], "paging": {"next": "https://api.sigfox.com/v2/devicetypes?page=2"}}'
        )
        page2_auth_error = MagicMock(status_code=403)
        
        mock_get.side_effect = [page1, page2_auth_error]
        
        sm = SigfoxManager("user", "pwd")
        
        with pytest.raises(SigfoxAuthError):
            sm.get_device_types(fetch_all_pages=True)
