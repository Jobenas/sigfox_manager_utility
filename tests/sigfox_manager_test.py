from unittest.mock import patch, MagicMock
from sigfox_manager.sigfox_manager import SigfoxManager
from sigfox_manager.models.schemas import ContractsResponse, DevicesResponse


class TestSigfoxManager:
    @patch("sigfox_manager.sigfox_manager.do_get")
    def test_get_contracts(self, mock_get):
        # Mock the API response
        mock_get.return_value = MagicMock(
            status_code=200, text='{"data": [{"id": "1", "name": "Contract 1"}]}'
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
        # Mock the API response
        mock_get.return_value = MagicMock(
            status_code=200, text='{"data": [{"id": "1", "name": "Device 1"}]}'
        )

        # Initialize SigfoxManager
        sm = SigfoxManager("user", "pwd")

        # Call the method
        response = sm.get_devices_by_contract("1")

        # Assert the response
        assert isinstance(response, DevicesResponse)
        assert response.data[0].id == "1"
        assert response.data[0].name == "Device 1"
