from base64 import b64encode

import requests
import json


class SigfoxManager:
	def __init__(self, user, pwd):
		self.user = user
		self.pwd = pwd
		self.auth = b64encode(f"{self.user}:{self.pwd}".encode('utf-8')).decode("ascii")
		self.devs_page = None

	def do_get(self, url):
		payload = {}
		headers = {
			'Authorization': f'Basic {self.auth}'
		}
		response = requests.get(url, headers=headers, data=payload)

		return response

	def do_post(self, url, payload, headers=None):
		if headers is None:
			headers = {
				'Authorization': f'Basic {self.auth}'
			}
		else:
			headers["Authorization"] = f'Basic {self.auth}'

		payload = json.dumps(payload)

		response = requests.post(url, data=payload, headers=headers)

		return response

	def get_contracts(self):
		contract_url = "https://api.sigfox.com/v2/contract-infos/"

		resp = self.do_get(contract_url)
		data = json.loads(resp.text)
		if resp.status_code == 200:
			data["status"] = "success"
		else:
			data["status"] = "error"

		return data

	def get_devices_by_contract(self, contract_id):
		devs_url = f"https://api.sigfox.com/v2/contract-infos/{contract_id}/devices"

		resp = self.do_get(devs_url)
		data = json.loads(resp.text)
		if resp.status_code == 200:
			data["status"] = "success"
			self.devs_page = data["paging"]
		else:
			data["status"] = "error"

		return data

	def get_device_info(self, dev_id):
		dev_url = f"https://api.sigfox.com/v2/devices/{dev_id}"

		resp = self.do_get(dev_url)
		data = json.loads(resp.text)
		if resp.status_code == 200:
			data["status"] = "success"
		else:
			data["status"] = "error"

		return data

	def get_device_messages(self, dev_id):
		msgs_url = f"https://api.sigfox.com/v2/devices/{dev_id}/messages"

		resp = self.do_get(msgs_url)
		data = json.loads(resp.text)
		if resp.status_code == 200:
			data["status"] = "success"
		else:
			data["status"] = "error"

		return data

	def create_device(self, dev_id, pac, dev_type_id, name, activable=True, lat=0.0, lng=0.0,
					  product_cert=None, prototype=False, automatic_renewal=True):
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

			"deviceTypeId": dev_type_id
		}

		if product_cert is not None and isinstance(product_cert, dict):
			if "key" in product_cert.keys():
				payload["productCertificate"] = product_cert

		headers = {
			"Content-Type": "application/json"
		}

		resp = self.do_post(dev_create_url, payload, headers)

		data = json.loads(resp.text)

		if resp.status_code == 200 or resp.status_code == 201:
			data["status"] = "success"
		else:
			data["status"] = "error"

		return data
