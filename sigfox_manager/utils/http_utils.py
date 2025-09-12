import json

import requests


def do_get(url: str, auth: bytes) -> requests.Response:
	"""
	Do an HTTP GET Request
	:param url: URL to perform the GET request to
	:param auth: Authorization header value
	:return: requests.Response object
	"""
	payload = {}
	headers = {
		"Authorization": f"Basic {auth}"
	}
	response = requests.get(url, headers=headers, data=payload)

	return response


def do_post(url: str, payload: dict, auth: bytes, headers: dict = dict()) -> requests.Response:
	"""
	Do an HTTP POST Request
	:param url: URL to perform the POST request to
	:param payload: JSON payload to send
	:param auth: Authorization header value
	:param headers: Additional headers to send
	:return: requests.Response object
	"""
	if headers is None:
		headers = {
			"Authorization": f"Basic {auth}"
		}
	else:
		headers["Authorization"] = f"Basic {auth}"

	payload_dict = json.dumps(payload)

	response = requests.post(url, data=payload_dict, headers=headers)

	return response
