from base64 import b64encode
from typing import Optional
import re

import json

from sigfox_manager.models.schemas import (
    ContractsResponse,
    DevicesResponse,
    Device,
    DeviceMessagesResponse,
    DeviceMessageStats,
    BaseDevice,
    DeviceTypesResponse,
)
from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import (
    SigfoxAPIException,
    SigfoxDeviceNotFoundError,
    SigfoxAuthError,
    SigfoxDeviceCreateConflictException,
    SigfoxDeviceTypeNotFoundException,
)
from sigfox_manager.utils.http_utils import do_get, do_post


class SigfoxManager:
    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.auth = b64encode(f"{self.user}:{self.pwd}".encode("utf-8")).decode("ascii")
        self.devs_page = None

    def get_contracts(self, fetch_all_pages: bool = True) -> ContractsResponse:
        """
        Get all contracts from Sigfox API the user can see
        :param fetch_all_pages: if True, fetches all pages automatically; if False, returns only first page
        :return: ContractsResponse object containing all contracts
        """
        contract_url = "https://api.sigfox.com/v2/contract-infos/"

        resp = do_get(contract_url, self.auth.encode("utf-8"))
        if resp.status_code != 200:
            raise SigfoxAPIException(
                status_code=resp.status_code, message="No Contract data found."
            )

        data = json.loads(resp.text)
        contracts_response = ContractsResponse(**data)
        
        # If pagination is enabled and there are more pages, fetch them all
        if fetch_all_pages and contracts_response.paging and contracts_response.paging.next:
            all_contracts = list(contracts_response.data)
            current_page = contracts_response
            
            while current_page.paging and current_page.paging.next:
                # Extract the next page URL
                next_url = current_page.paging.next
                
                resp = do_get(next_url, self.auth.encode("utf-8"))
                
                if resp.status_code != 200:
                    # If we can't get a page, break and return what we have
                    break
                    
                data = json.loads(resp.text)
                current_page = ContractsResponse(**data)
                all_contracts.extend(current_page.data)
            
            # Create a new response with all contracts and clear pagination
            from .models.schemas import Paging
            contracts_response.data = all_contracts
            contracts_response.paging = Paging(next=None)

        return contracts_response

    def get_devices_by_contract(self, contract_id: str, fetch_all_pages: bool = True) -> DevicesResponse:
        """
        Get all the devices associated with a contract ID
        :param contract_id: string containing the contract ID to search for
        :param fetch_all_pages: if True, fetches all pages automatically; if False, returns only first page
        :return: DevicesResponse object containing the information for all the devices associated with the contract
        """
        devs_url = f"https://api.sigfox.com/v2/contract-infos/{contract_id}/devices"

        resp = do_get(devs_url, self.auth.encode("utf-8"))

        if resp.status_code != 200:
            raise SigfoxDeviceNotFoundError

        data = json.loads(resp.text)
        devices_response = DevicesResponse(**data)
        
        # If pagination is enabled and there are more pages, fetch them all
        if fetch_all_pages and devices_response.paging and devices_response.paging.next:
            all_devices = list(devices_response.data)
            current_page = devices_response
            
            while current_page.paging and current_page.paging.next:
                # Extract the next page URL
                next_url = current_page.paging.next
                
                resp = do_get(next_url, self.auth.encode("utf-8"))
                
                if resp.status_code != 200:
                    # If we can't get a page, break and return what we have
                    break
                    
                data = json.loads(resp.text)
                current_page = DevicesResponse(**data)
                all_devices.extend(current_page.data)
            
            # Create a new response with all devices and clear pagination
            from .models.schemas import Paging
            devices_response.data = all_devices
            devices_response.paging = Paging(next=None)

        return devices_response

    def get_device_info(self, dev_id: str) -> Device:
        """
        Gets the detailed information for a specific device by its ID.
        :param dev_id: string containing the Sigfox ID for the selected device.
        :return: Device object describing the requested device.
        """
        dev_url = f"https://api.sigfox.com/v2/devices/{dev_id}"

        resp = do_get(dev_url, self.auth.encode("utf-8"))

        if resp.status_code == 403:
            raise SigfoxAuthError
        elif resp.status_code == 404:
            raise SigfoxDeviceNotFoundError

        data = json.loads(resp.text)
        device = Device(**data)

        return device

    def get_device_messages(
        self, dev_id: str, threshold: Optional[int] = None
    ) -> DeviceMessagesResponse:
        """
        Retrieves a list of messages for the specified device. An optional parameter of threshold can define the
        starting point for the message list.
        :param dev_id: string containing the Sigfox ID for the selected device.
        :param threshold: timestamp value in epoch that shows the starting point for the query, if no value is provided
        the query grabs all messages available in the backend.
        :return: List of messages for the device, contained in the Device<essageResponse
        """
        if threshold is None:
            msgs_url = f"https://api.sigfox.com/v2/devices/{dev_id}/messages"
        else:
            msgs_url = (
                f"https://api.sigfox.com/v2/devices/{dev_id}/messages?since={threshold}"
            )

        resp = do_get(msgs_url, self.auth.encode("utf-8"))

        if resp.status_code == 403:
            raise SigfoxAuthError
        elif resp.status_code == 404:
            raise SigfoxDeviceNotFoundError

        data = json.loads(resp.text)
        messages = DeviceMessagesResponse(**data)

        return messages

    def get_device_message_number(self, dev_id) -> DeviceMessageStats:
        """
        Returns message metrics for the specified device.
        :param dev_id: string containing the Sigfox ID for the selected device.
        :return: DeviceMessageStats object that shows message transmission metrics.
        """
        metric_url = f"https://api.sigfox.com/v2/devices/{dev_id}/messages/metric"
        resp = do_get(metric_url, self.auth.encode("utf-8"))
        if resp.status_code == 403:
            raise SigfoxAuthError
        elif resp.status_code == 404:
            raise SigfoxDeviceNotFoundError

        data = json.loads(resp.text)
        message_stats = DeviceMessageStats(**data)

        return message_stats

    def create_device(
        self,
        dev_id,
        pac,
        dev_type_id,
        name,
        activable=True,
        lat=0.0,
        lng=0.0,
        product_cert=None,
        prototype=False,
        automatic_renewal=True,
    ) -> BaseDevice:
        """
        Creates a new device in the Sigfox backend.
        :param dev_id: string containing the HEX value of the Sigfox ID.
        :param pac: string containing the HEX value of the sigfox PAC.
        :param dev_type_id: string containing the Sigfox device type ID.
        :param name: name for the device.
        :param activable: bool value that determines if the device is activable.
        :param lat: float corresponding to the latitude of the device.
        :param lng: float corresponding to the longitude of the device.
        :param product_cert: dictionary containing the product certificate for the device.
        :param prototype: bool value that determines if the device is a prototype.
        :param automatic_renewal: bool value that determines if the device has automatic renewal.
        :return: BaseDevice object containing the information for the newly created device.
        """
        dev_create_url = "https://api.sigfox.com/v2/devices/"
        payload = {
            "id": dev_id,
            "name": name,
            "pac": pac,
            "lat": lat,
            "lng": lng,
            "automatic_renewal": automatic_renewal,
            "activable": activable,
            "prototype": prototype,
            "deviceTypeId": dev_type_id,
        }

        if product_cert is not None and isinstance(product_cert, dict):
            if "key" in product_cert.keys():
                payload["productCertificate"] = product_cert

        headers = {"Content-Type": "application/json"}

        resp = do_post(
            dev_create_url, payload, self.auth.encode("utf-8"), headers=headers
        )

        if resp.status_code == 403:
            raise SigfoxAuthError
        elif resp.status_code == 409:
            raise SigfoxDeviceCreateConflictException

        data = json.loads(resp.text)

        base_device = BaseDevice(**data)

        return base_device

    def get_device_types(self, fetch_all_pages: bool = True) -> DeviceTypesResponse:
        """
        GET /v2/devicetypes
        - When fetch_all_pages=True, follow paging.next and merge all pages,
          returning a DeviceTypesResponse with paging.next=None and full data list.
        - Map 403 -> SigfoxAuthError; re-raise other HTTP errors consistently with existing style.
        :param fetch_all_pages: if True, fetches all pages automatically; if False, returns only first page
        :return: DeviceTypesResponse object containing all device types
        """
        device_types_url = "https://api.sigfox.com/v2/devicetypes"

        resp = do_get(device_types_url, self.auth.encode("utf-8"))
        
        if resp.status_code == 403:
            raise SigfoxAuthError
        elif resp.status_code != 200:
            raise SigfoxAPIException(
                status_code=resp.status_code, message="Failed to fetch device types."
            )

        data = json.loads(resp.text)
        device_types_response = DeviceTypesResponse(**data)
        
        # If pagination is enabled and there are more pages, fetch them all
        if fetch_all_pages and device_types_response.paging and device_types_response.paging.next:
            all_device_types = list(device_types_response.data)
            current_page = device_types_response
            
            while current_page.paging and current_page.paging.next:
                # Extract the next page URL
                next_url = current_page.paging.next
                
                resp = do_get(next_url, self.auth.encode("utf-8"))
                
                if resp.status_code == 403:
                    raise SigfoxAuthError
                elif resp.status_code != 200:
                    # If we can't get a page, break and return what we have
                    break
                    
                data = json.loads(resp.text)
                current_page = DeviceTypesResponse(**data)
                all_device_types.extend(current_page.data)
            
            # Create a new response with all device types and clear pagination
            from .models.schemas import Paging
            device_types_response.data = all_device_types
            device_types_response.paging = Paging(next=None)

        return device_types_response

    def resolve_device_type_id(self, ref: str) -> str:
        """
        Resolve a device type reference to its id.
        - If `ref` looks like an id (hex-ish / UUID-like), check existence among device types; return it if present.
        - Else treat `ref` as a name (exact, case-sensitive match) and return the id.
        - Raise SigfoxDeviceTypeNotFoundException if not found.
        - Uses get_device_types(fetch_all_pages=True) to obtain the catalog.
        :param ref: Device type id or name to resolve
        :return: Device type id
        :raises SigfoxDeviceTypeNotFoundException: if device type cannot be resolved
        """
        device_types_response = self.get_device_types(fetch_all_pages=True)
        device_types = device_types_response.data
        
        # First, try to match by id (exact match)
        for dt in device_types:
            if dt.id and dt.id == ref:
                return dt.id
        
        # If not found by id, try to match by name (exact, case-sensitive)
        for dt in device_types:
            if dt.name == ref and dt.id:
                return dt.id
        
        # If still not found, raise exception
        raise SigfoxDeviceTypeNotFoundException(
            f"Device type not found: {ref}"
        )

    def provision_device(
        self,
        dev_id: str,
        pac: str,
        dev_type_ref: str,
        name: Optional[str] = None,
        **kwargs
    ) -> BaseDevice:
        """
        Validate inputs, resolve device type, and call create_device.
        Validation:
          - dev_id: uppercase hex (3..16 chars) — raise ValueError if invalid
          - pac: 16-char alphanumeric — raise ValueError if invalid
          - dev_type_ref: resolve via resolve_device_type_id(); raise SigfoxDeviceTypeNotFoundException on failure
        Then delegate to existing create_device(...), passing dev_type_id and optional kwargs (e.g., prototype, automatic_renewal, lat/lng).
        Returns BaseDevice.
        :param dev_id: Sigfox device ID (uppercase hex, 3-16 chars)
        :param pac: PAC code (16-char alphanumeric)
        :param dev_type_ref: Device type id or name
        :param name: Optional device name
        :param kwargs: Additional parameters to pass to create_device (prototype, automatic_renewal, lat, lng, etc.)
        :return: BaseDevice object
        :raises ValueError: if dev_id or pac format is invalid
        :raises SigfoxDeviceTypeNotFoundException: if device type cannot be resolved
        """
        # Validate dev_id: uppercase hex (3..16 chars)
        dev_id_pattern = re.compile(r'^[0-9A-F]{3,16}$')
        if not dev_id_pattern.match(dev_id):
            raise ValueError(
                f"Invalid dev_id format: {dev_id}. Must be uppercase hex, 3-16 characters."
            )
        
        # Validate pac: 16-char alphanumeric
        pac_pattern = re.compile(r'^[0-9A-Za-z]{16}$')
        if not pac_pattern.match(pac):
            raise ValueError(
                f"Invalid pac format: {pac}. Must be 16 alphanumeric characters."
            )
        
        # Resolve device type
        dev_type_id = self.resolve_device_type_id(dev_type_ref)
        
        # Extract known parameters from kwargs or use defaults
        activable = kwargs.pop('activable', True)
        lat = kwargs.pop('lat', 0.0)
        lng = kwargs.pop('lng', 0.0)
        product_cert = kwargs.pop('product_cert', None)
        prototype = kwargs.pop('prototype', False)
        automatic_renewal = kwargs.pop('automatic_renewal', True)
        
        # Call create_device with resolved parameters
        return self.create_device(
            dev_id=dev_id,
            pac=pac,
            dev_type_id=dev_type_id,
            name=name if name else dev_id,  # Use dev_id as name if not provided
            activable=activable,
            lat=lat,
            lng=lng,
            product_cert=product_cert,
            prototype=prototype,
            automatic_renewal=automatic_renewal
        )
