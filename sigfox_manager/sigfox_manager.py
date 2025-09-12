from base64 import b64encode
from typing import Optional

import json

from sigfox_manager.models.schemas import (
    ContractsResponse,
    DevicesResponse,
    Device,
    DeviceMessagesResponse,
    DeviceMessageStats,
    BaseDevice,
)
from sigfox_manager.sigfox_manager_exceptions.sigfox_exceptions import (
    SigfoxAPIException,
    SigfoxDeviceNotFoundError,
    SigfoxAuthError,
    SigfoxDeviceCreateConflictException,
)
from sigfox_manager.utils.http_utils import do_get, do_post


class SigfoxManager:
    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.auth = b64encode(f"{self.user}:{self.pwd}".encode("utf-8")).decode("ascii")
        self.devs_page = None

    def get_contracts(self) -> ContractsResponse:
        """
        Get all contracts from Sigfox API the user can see
        :return:
        """
        contract_url = "https://api.sigfox.com/v2/contract-infos/"

        resp = do_get(contract_url, self.auth.encode("utf-8"))
        if resp.status_code != 200:
            raise SigfoxAPIException(
                status_code=resp.status_code, message="No Contract data found."
            )

        data = json.loads(resp.text)
        return ContractsResponse(**data)

    def get_devices_by_contract(self, contract_id: str) -> DevicesResponse:
        """
        Get all the devices associated with a contract ID
        :param contract_id: string containing the contract ID to search for
        :return: DevicesResponse object containing the information for all the devices associated with the contract
        """
        devs_url = f"https://api.sigfox.com/v2/contract-infos/{contract_id}/devices"

        resp = do_get(devs_url, self.auth.encode("utf-8"))

        if resp.status_code != 200:
            raise SigfoxDeviceNotFoundError

        data = json.loads(resp.text)
        devices_response = DevicesResponse(**data)

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
