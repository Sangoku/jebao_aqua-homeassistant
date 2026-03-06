#!/usr/bin/env python3
"""
Debug script to test mode changes on Jebao Aqua Wavemaker
Device: 1.0 W_8AE4F4
Product Key: 54114ccdac1e41c0bb17e222887c07ba
Device ID: fw1iMEpzecdyMiKjdtt7hS

This script helps reverse engineer how the device changes modes by:
1. Reading current device state
2. Sending different mode values
3. Logging all requests and responses
4. Testing both cloud API and local communication
"""

import asyncio
import aiohttp
import json
import logging
import sys
import ssl
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'mode_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
LOGGER = logging.getLogger(__name__)

# Device Configuration
DEVICE_ID = "fw1iMEpzecdyMiKjdtt7hS"
DEVICE_IP = "192.168.0.237"
PRODUCT_KEY = "54114ccdac1e41c0bb17e222887c07ba"
LAN_PORT = 12416

# Gizwits API Configuration
GIZWITS_APP_ID = "c3703c4888ec4736a3a0d9425c321604"
TIMEOUT = aiohttp.ClientTimeout(total=10)
LOGIN_URL = "https://euaepapp.gizwits.com/app/smart_home/login/pwd"
API_BASE = "https://euapi.gizwits.com/app"

# Mode definitions (from model)
MODES = {
    0: "经典造浪 (Square Wave / Classic)",
    1: "正弦造浪 (Sine Wave)",
    2: "随机造浪 (Random Wave)",
    3: "恒流造浪 (Constant Flow)"
}

class ModeDebugger:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.token = None
        self.session = None
        
    async def __aenter__(self):
        # Create SSL context that doesn't verify certificates (for debugging only)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self):
        """Login to Gizwits API"""
        url = LOGIN_URL
        data = {
            "appKey": GIZWITS_APP_ID,
            "data": {
                "account": self.email,
                "password": self.password,
                "lang": "en",
                "refreshToken": True,
            },
            "version": "1.0",
        }
        headers = {
            "X-Gizwits-Application-Id": GIZWITS_APP_ID,
            "Content-Type": "application/json",
        }
        
        LOGGER.info("=" * 80)
        LOGGER.info("LOGGING IN")
        LOGGER.info("=" * 80)
        
        try:
            async with self.session.post(url, json=data, headers=headers, timeout=TIMEOUT) as response:
                response_text = await response.text()
                LOGGER.debug(f"Login response status: {response.status}")
                LOGGER.debug(f"Login response: {response_text}")
                
                json_response = json.loads(response_text)
                if json_response.get("error", False):
                    LOGGER.error(f"Login failed: {json_response}")
                    return False
                    
                self.token = json_response.get("data", {}).get("userToken")
                if self.token:
                    LOGGER.info(f"✓ Login successful! Token: {self.token[:20]}...")
                    return True
                else:
                    LOGGER.error("No token received")
                    return False
                    
        except Exception as e:
            LOGGER.error(f"Login exception: {e}")
            return False
    
    async def get_device_status(self):
        """Get current device status via cloud API"""
        url = f"{API_BASE}/devdata/{DEVICE_ID}/latest"
        headers = {
            "X-Gizwits-User-token": self.token,
            "X-Gizwits-Application-Id": GIZWITS_APP_ID,
            "Accept": "application/json",
        }
        
        LOGGER.info("=" * 80)
        LOGGER.info("READING CURRENT DEVICE STATUS")
        LOGGER.info("=" * 80)
        
        try:
            async with self.session.get(url, headers=headers, timeout=TIMEOUT) as response:
                result = await response.text()
                LOGGER.debug(f"Status response: {result}")
                
                if response.status == 200:
                    data = json.loads(result)
                    attrs = data.get("attr", {})
                    
                    LOGGER.info("Current device attributes:")
                    for key, value in attrs.items():
                        LOGGER.info(f"  {key}: {value}")
                    
                    if "Mode" in attrs:
                        mode_val = attrs["Mode"]
                        LOGGER.info(f"  → Current Mode: {mode_val} ({MODES.get(mode_val, 'Unknown')})")
                    
                    return attrs
                else:
                    LOGGER.error(f"Failed to get status: {response.status}")
                    return None
        except Exception as e:
            LOGGER.error(f"Exception getting status: {e}")
            return None
    
    async def set_mode(self, mode_value: int):
        """Set device mode via cloud API"""
        url = f"{API_BASE}/control/{DEVICE_ID}"
        headers = {
            "X-Gizwits-User-token": self.token,
            "X-Gizwits-Application-Id": GIZWITS_APP_ID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # According to the model, Mode is an enum at byte 0, bit offset 5, length 2 bits
        data = {"attrs": {"Mode": mode_value}}
        
        LOGGER.info("=" * 80)
        LOGGER.info(f"SETTING MODE TO: {mode_value} ({MODES.get(mode_value, 'Unknown')})")
        LOGGER.info("=" * 80)
        LOGGER.info(f"Request URL: {url}")
        LOGGER.info(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            async with self.session.post(url, json=data, headers=headers, timeout=TIMEOUT) as response:
                result = await response.text()
                LOGGER.info(f"Response status: {response.status}")
                LOGGER.info(f"Response body: {result}")
                
                if response.status == 200:
                    LOGGER.info("✓ Command sent successfully!")
                    return True
                else:
                    LOGGER.error(f"✗ Command failed with status: {response.status}")
                    return False
        except Exception as e:
            LOGGER.error(f"✗ Exception sending command: {e}")
            return False
    
    async def test_local_connection(self):
        """Test local device connection and raw protocol"""
        LOGGER.info("=" * 80)
        LOGGER.info("TESTING LOCAL CONNECTION")
        LOGGER.info("=" * 80)
        LOGGER.info(f"Connecting to {DEVICE_IP}:{LAN_PORT}")
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(DEVICE_IP, LAN_PORT),
                timeout=5.0
            )
            
            LOGGER.info("✓ TCP connection established")
            
            # Send initial handshake
            await self._send_local_command(writer, b"\x00\x06")
            response = await reader.read(1024)
            LOGGER.info(f"Handshake response (hex): {response.hex()}")
            
            binding_key = response[-12:]
            LOGGER.info(f"Binding key: {binding_key.hex()}")
            
            # Authenticate
            await self._send_local_command(writer, b"\x00\x08", binding_key)
            auth_response = await reader.read(1024)
            LOGGER.info(f"Auth response (hex): {auth_response.hex()}")
            
            # Request device status
            await self._send_local_command(writer, b"\x00\x93", b"\x00\x00\x00\x02\x02")
            status_response = await reader.read(1024)
            LOGGER.info(f"Status response (hex): {status_response.hex()}")
            LOGGER.info(f"Status response length: {len(status_response)} bytes")
            
            # Parse the status
            self._parse_status_response(status_response)
            
            writer.close()
            await writer.wait_closed()
            LOGGER.info("✓ Connection closed")
            
        except asyncio.TimeoutError:
            LOGGER.error("✗ Connection timeout")
        except Exception as e:
            LOGGER.error(f"✗ Local connection error: {e}")
    
    async def _send_local_command(self, writer, command, payload=b""):
        """Send a command to the local device"""
        header = b"\x00\x00\x00\x03"
        flag = b"\x00"
        length = len(flag + command + payload).to_bytes(1, byteorder="big")
        packet = header + length + flag + command + payload
        
        LOGGER.debug(f"Sending command: {command.hex()}, payload: {payload.hex()}")
        LOGGER.debug(f"Full packet (hex): {packet.hex()}")
        writer.write(packet)
        await writer.drain()
    
    def _parse_status_response(self, response):
        """Parse status response and extract mode information"""
        try:
            # Find the device status payload
            pattern = b"\x00\x00\x00\x03"
            start_index = response.rfind(pattern)
            if start_index == -1:
                LOGGER.error("Status pattern not found in response")
                return
            
            # Extract payload (simplified - actual parsing is complex)
            payload_start = start_index + 4 + 1 + 1 + 2  # header + length + flag + command
            if payload_start < len(response):
                payload = response[payload_start:]
                LOGGER.info(f"Device status payload (hex): {payload.hex()}")
                
                # Byte 0 contains the mode at bits 5-6 (2 bits)
                if len(payload) > 0:
                    byte0 = payload[0]
                    LOGGER.info(f"Byte 0 (binary): {bin(byte0)[2:].zfill(8)}")
                    
                    # Extract mode (bits 5-6, 2 bits)
                    mode = (byte0 >> 5) & 0b11
                    LOGGER.info(f"Extracted mode value: {mode} ({MODES.get(mode, 'Unknown')})")
                    
                    # Show all bits
                    LOGGER.info("Byte 0 bit breakdown:")
                    LOGGER.info(f"  Bit 0 (SwitchON): {(byte0 >> 0) & 1}")
                    LOGGER.info(f"  Bit 1 (PulseTide): {(byte0 >> 1) & 1}")
                    LOGGER.info(f"  Bit 2 (FeedSwitch): {(byte0 >> 2) & 1}")
                    LOGGER.info(f"  Bit 3 (TimerON): {(byte0 >> 3) & 1}")
                    LOGGER.info(f"  Bits 5-6 (Mode): {mode}")
                    LOGGER.info(f"  Bits 7-8 (Linkage): {(byte0 >> 7) & 0b11}")
                    
                if len(payload) > 2:
                    LOGGER.info(f"Byte 2 (Flow): {payload[2]}%")
                if len(payload) > 3:
                    LOGGER.info(f"Byte 3 (Frequency): {payload[3]}")
                if len(payload) > 4:
                    LOGGER.info(f"Byte 4 (FeedTime): {payload[4]} mins")
                    
        except Exception as e:
            LOGGER.error(f"Error parsing status: {e}")
    
    async def run_mode_tests(self):
        """Run comprehensive mode change tests"""
        LOGGER.info("*" * 80)
        LOGGER.info("JEBAO AQUA MODE DEBUG SCRIPT")
        LOGGER.info(f"Device: {DEVICE_ID}")
        LOGGER.info(f"IP: {DEVICE_IP}")
        LOGGER.info("*" * 80)
        
        # Login
        if not await self.login():
            LOGGER.error("Failed to login, aborting tests")
            return
        
        # Get initial status
        print("\n" + "=" * 80)
        print("STEP 1: Reading initial device status...")
        print("=" * 80)
        initial_status = await self.get_device_status()
        
        if initial_status:
            current_mode = initial_status.get("Mode")
            print(f"\n✓ Initial mode: {current_mode} ({MODES.get(current_mode, 'Unknown')})")
        
        # Wait before testing
        await asyncio.sleep(2)
        
        # Test each mode
        print("\n" + "=" * 80)
        print("STEP 2: Testing each mode value...")
        print("=" * 80)
        
        for mode_val in [0, 1, 2, 3]:
            print(f"\n--- Testing Mode {mode_val}: {MODES.get(mode_val, 'Unknown')} ---")
            
            success = await self.set_mode(mode_val)
            
            if success:
                print(f"✓ Command sent for mode {mode_val}")
                print(f"  → Please check your app to confirm the device changed to: {MODES[mode_val]}")
                
                # Wait a bit then read status back
                await asyncio.sleep(3)
                
                # Verify via API
                status = await self.get_device_status()
                if status:
                    reported_mode = status.get("Mode")
                    if reported_mode == mode_val:
                        print(f"  ✓ API confirms mode is now: {reported_mode}")
                    else:
                        print(f"  ✗ API reports different mode: {reported_mode} (expected {mode_val})")
            else:
                print(f"✗ Failed to send command for mode {mode_val}")
            
            # Wait before next test
            input("\nPress Enter to test next mode...")
        
        # Test local connection
        print("\n" + "=" * 80)
        print("STEP 3: Testing local TCP connection...")
        print("=" * 80)
        await self.test_local_connection()
        
        print("\n" + "=" * 80)
        print("TESTS COMPLETE")
        print("=" * 80)
        print(f"Check the log file for detailed protocol information")


async def main():
    """Main entry point"""
    print("=" * 80)
    print("JEBAO AQUA MODE DEBUGGER")
    print("=" * 80)
    print()
    
    # Get credentials
    email = input("Enter your Gizwits email: ").strip()
    if not email:
        print("Email required!")
        return
    
    password = input("Enter your Gizwits password: ").strip()
    if not password:
        print("Password required!")
        return
    
    print()
    print("Starting mode debug tests...")
    print("The script will:")
    print("  1. Login to Gizwits")
    print("  2. Read current device status")
    print("  3. Test each mode (0, 1, 2, 3)")
    print("  4. Test local TCP connection")
    print()
    print("Please monitor your Jebao app to confirm mode changes!")
    print()
    input("Press Enter to begin...")
    
    async with ModeDebugger(email, password) as debugger:
        await debugger.run_mode_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        LOGGER.error(f"Unhandled exception: {e}", exc_info=True)