import json
from datetime import datetime, timedelta

from sigfox_manager import SigfoxManager
from pprint import pprint

if __name__ == '__main__':
	f = open("configuration.conf", "r")
	data = f.read()
	f.close()

	data = data.split("\n")

	user = data[0].split(":")[1]
	pwd = data[1].split(":")[1]

	sm = SigfoxManager(user, pwd)

	# contracts = sm.get_contracts()
	#
	# if contracts["status"] == "success":
	# 	for contract in contracts["data"]:
	# 		if contract["name"] == "EAT - ELECTRODUNAS":
	# 			devs = sm.get_devices_by_contract(contract["id"])
	# 			if devs["status"] == "success":
	# 				pprint(devs["data"])

	device_id = "3EA68B"

	ts_threshold = int((datetime.now() - timedelta(seconds=3600)).timestamp()) * 1000

	metrics = sm.get_device_message_number(device_id)
	pprint(metrics)

	msgs = sm.get_device_messages(device_id, ts_threshold)
	pprint(msgs)
	pprint(msgs["data"][0])
	# pprint(msg_data["data"][-1])

	# # device_id = "23DE415"
	# # dev_data = sm.get_device_info(device_id)
	# #
	# # pprint(dev_data)
	# #
	# # dev_msgs = sm.get_device_messages(device_id)
	# #
	# # pprint(dev_msgs)
	#
	# result = sm.create_device(dev_id="23DE415",
	# 						  pac="18AFFC184633697B",
	# 						  dev_type_id="5fdb8def25643206e801a7d7",
	# 						  name="ECM-PL Prototype 2",
	# 						  prototype=True)
	#
	# pprint(result)
