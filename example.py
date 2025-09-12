#!/usr/bin/env python3
"""
Example usage of the Sigfox Manager library.

This example demonstrates how to:
1. Initialize the SigfoxManager with credentials
2. Retrieve contracts and devices
3. Get device information and messages
4. Create new devices

Before running this example:
1. Replace YOUR_USERNAME and YOUR_PASSWORD with your actual Sigfox API credentials
2. Replace DEVICE_ID_HERE with an actual device ID from your account
3. Replace the device creation parameters with your actual values

For more information, visit: https://github.com/Jobenas/sigfox_manager_utility
"""

import os
from datetime import datetime, timedelta
from pprint import pprint

from sigfox_manager import SigfoxManager, SigfoxAPIException


def main():
    """Main example function demonstrating Sigfox Manager usage."""
    
    # Initialize with your credentials
    # Option 1: Replace with your actual credentials
    user = "YOUR_USERNAME"  # Replace with your Sigfox API username
    pwd = "YOUR_PASSWORD"   # Replace with your Sigfox API password
    
    # Option 2: Use environment variables (recommended for security)
    # user = os.getenv("SIGFOX_USER")
    # pwd = os.getenv("SIGFOX_PASSWORD")
    
    if user == "YOUR_USERNAME" or pwd == "YOUR_PASSWORD":
        print("⚠️  Please update the credentials in this example before running!")
        print("   Replace YOUR_USERNAME and YOUR_PASSWORD with your actual Sigfox API credentials.")
        return
    
    try:
        # Create SigfoxManager instance
        manager = SigfoxManager(user, pwd)
        print("✅ SigfoxManager initialized successfully")
        
        # Get all contracts
        print("\n📋 Fetching contracts...")
        contracts = manager.get_contracts()
        print(f"Found {len(contracts.data)} contracts")
        
        # Display contract information
        for contract in contracts.data:
            print(f"  📄 Contract: {contract.name} (ID: {contract.id})")
            
            # Get devices for this contract
            try:
                devices = manager.get_devices_by_contract(contract.id)
                print(f"    📱 Found {len(devices.data)} devices")
                
                # Show first few devices
                for i, device in enumerate(devices.data[:3]):  # Show max 3 devices
                    print(f"    📱 Device {i+1}: {device.name} (ID: {device.id})")
                    
            except SigfoxAPIException as e:
                print(f"    ❌ Error fetching devices for contract {contract.name}: {e}")
        
        # Example: Get specific device information
        # Replace with an actual device ID from your account
        device_id = "DEVICE_ID_HERE"  # Replace with actual device ID
        
        if device_id != "DEVICE_ID_HERE":
            print(f"\n📱 Getting information for device {device_id}...")
            
            try:
                # Get device details
                device_info = manager.get_device_info(device_id)
                print(f"  Device Name: {device_info.name}")
                print(f"  Device Type: {device_info.deviceType}")
                
                # Get device message statistics
                message_stats = manager.get_device_message_number(device_id)
                print(f"  Total Messages: {message_stats}")
                
                # Get recent messages (last hour)
                print(f"\n📨 Getting recent messages for device {device_id}...")
                messages = manager.get_device_messages(device_id)
                
                if messages.data:
                    print(f"  Found {len(messages.data)} messages")
                    
                    # Show the most recent message
                    latest_message = messages.data[0]
                    timestamp = datetime.fromtimestamp(latest_message.time / 1000)
                    print(f"  Latest message:")
                    print(f"    📅 Time: {timestamp}")
                    print(f"    📊 Data: {latest_message.data}")
                    print(f"    🔢 Sequence: {latest_message.seqNumber}")
                else:
                    print("  No messages found")
                    
            except SigfoxAPIException as e:
                print(f"  ❌ Error fetching device information: {e}")
        else:
            print("\n⚠️  To test device-specific operations, replace 'DEVICE_ID_HERE' with an actual device ID")
        
        # Example: Create a new device (commented out for safety)
        print(f"\n🆕 Device creation example (commented out for safety):")
        print("# To create a device, uncomment and modify the following:")
        print("# result = manager.create_device(")
        print("#     dev_id='YOUR_DEVICE_ID',")
        print("#     pac='YOUR_PAC_CODE',")
        print("#     dev_type_id='YOUR_DEVICE_TYPE_ID',")
        print("#     name='Your Device Name',")
        print("#     prototype=True")
        print("# )")
        print("# print(f'Device created: {result}')")
        
    except SigfoxAPIException as e:
        print(f"❌ Sigfox API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    main()
