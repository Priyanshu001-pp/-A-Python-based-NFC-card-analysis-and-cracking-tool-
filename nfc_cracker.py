#!/usr/bin/env python3
# NFC Cracker - A tool for NFC card analysis and cracking
# Author: AI Assistant

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from colorama import init, Fore, Style
from tqdm import tqdm
import random

# Initialize colorama
init()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("nfc_cracker.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# Add simulation mode flag
SIMULATION_MODE = False

try:
    import nfc
    from nfc.clf import RemoteTarget
except ImportError:
    print(f"{Fore.RED}Error: Required module 'nfcpy' not found.{Style.RESET_ALL}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Simulation classes for when no hardware is available
class SimulatedTag:
    """A simulated NFC tag for testing without hardware"""
    def __init__(self, tag_type="MIFARE Classic 1K"):
        self.product = tag_type
        self.identifier = bytes([random.randint(0, 255) for _ in range(4)])
        self.size = 1024 if "1K" in tag_type else 4096
        self._sectors = {}
        self._keys = {}

        # Initialize with some default data
        for sector in range(16):  # 16 sectors for MIFARE Classic 1K
            # Set default keys for some sectors
            if sector < 5:
                self._keys[sector] = {
                    'A': bytes.fromhex("FFFFFFFFFFFF"),
                    'B': bytes.fromhex("FFFFFFFFFFFF")
                }
            elif sector < 10:
                self._keys[sector] = {
                    'A': bytes.fromhex("A0A1A2A3A4A5"),
                    'B': bytes.fromhex("B0B1B2B3B4B5")
                }
            else:
                self._keys[sector] = {
                    'A': None,
                    'B': None
                }

            # Create some random data for each sector
            self._sectors[sector] = [
                bytes([random.randint(0, 255) for _ in range(16)]) for _ in range(4)
            ]

            # First block of first sector contains UID
            if sector == 0:
                self._sectors[0][0] = self.identifier + bytes([random.randint(0, 255) for _ in range(12)])

    def authenticate(self, sector, key, key_type_a=True):
        """Simulate authentication with a sector"""
        key_type = 'A' if key_type_a else 'B'

        # If we don't have a key for this sector, authentication always fails
        if sector not in self._keys or self._keys[sector][key_type] is None:
            return False

        # If the key matches, authentication succeeds
        return key == self._keys[sector][key_type]

    def read(self, block):
        """Simulate reading a block"""
        sector = block // 4
        block_in_sector = block % 4

        # If we don't have data for this sector, reading fails
        if sector not in self._sectors:
            raise Exception("Failed to read block")

        return self._sectors[sector][block_in_sector]

class SimulatedDevice:
    """A simulated NFC reader for testing without hardware"""
    def __init__(self):
        self.name = "Simulated NFC Reader"

    def sense(self, target_type):
        """Simulate sensing a card"""
        # 80% chance of finding a card
        if random.random() < 0.8:
            return "Simulated Card"
        return None

    def close(self):
        """Simulate closing the device"""
        pass

class NFCCracker:
    def __init__(self, args):
        self.args = args
        self.device = None
        self.known_keys = self._load_keys(args.key_file)
        self.simulation = args.simulation

    def _load_keys(self, key_file):
        """Load known keys from file"""
        keys = []
        if key_file and os.path.exists(key_file):
            try:
                with open(key_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            keys.append(bytes.fromhex(line))
                logger.info(f"Loaded {len(keys)} keys from {key_file}")
            except Exception as e:
                logger.error(f"Error loading keys: {e}")

        # Add default keys
        default_keys = [
            bytes.fromhex("FFFFFFFFFFFF"),  # Default key
            bytes.fromhex("000000000000"),  # All zeros
            bytes.fromhex("A0A1A2A3A4A5"),  # Common key
            bytes.fromhex("B0B1B2B3B4B5"),  # Common key
            bytes.fromhex("D3F7D3F7D3F7"),  # Common key
        ]

        for key in default_keys:
            if key not in keys:
                keys.append(key)

        return keys

    def connect(self):
        """Connect to NFC reader"""
        if self.simulation:
            logger.info("Running in simulation mode - using simulated NFC reader")
            self.device = SimulatedDevice()
            logger.info(f"Connected to {self.device.name}")
            return True

        try:
            logger.info("Connecting to NFC reader...")
            self.device = nfc.ContactlessFrontend('usb')
            logger.info(f"Connected to {self.device}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NFC reader: {e}")
            return False

    def scan_for_targets(self):
        """Scan for NFC targets"""
        if not self.device:
            logger.error("No NFC device connected")
            return None

        logger.info("Scanning for NFC targets...")
        try:
            if self.simulation:
                # In simulation mode, just return a simulated target
                time.sleep(1)  # Simulate scanning time
                target = self.device.sense(None)
                if target:
                    logger.info(f"Found simulated target")
                    return target
                else:
                    logger.warning("No NFC targets found")
                    return None

            # Scan for various NFC card types
            target_types = [
                RemoteTarget('106A'),  # ISO14443A (MIFARE, NXP)
                RemoteTarget('106B'),  # ISO14443B
                RemoteTarget('212F'),  # FeliCa
            ]

            for target_type in target_types:
                target = self.device.sense(target_type)
                if target:
                    logger.info(f"Found target: {target}")
                    return target

            logger.warning("No NFC targets found")
            return None
        except Exception as e:
            logger.error(f"Error scanning for targets: {e}")
            return None

    def analyze_card(self, target):
        """Analyze the detected NFC card"""
        if not target:
            return

        print(f"\n{Fore.GREEN}=== NFC Card Analysis ==={Style.RESET_ALL}")

        if self.simulation:
            print(f"Card Type: {Fore.YELLOW}Simulated MIFARE Classic 1K{Style.RESET_ALL}")
            # Create a simulated tag
            tag = SimulatedTag()
            print(f"Tag Type: {Fore.YELLOW}{tag.product}{Style.RESET_ALL}")
            print(f"UID: {Fore.CYAN}{tag.identifier.hex().upper()}{Style.RESET_ALL}")
            self._crack_mifare_classic(tag)
            return

        print(f"Card Type: {Fore.YELLOW}{target}{Style.RESET_ALL}")

        # Connect to the card
        try:
            tag = nfc.tag.activate(self.device, target)
            print(f"Tag Type: {Fore.YELLOW}{tag}{Style.RESET_ALL}")

            # Display card information
            if hasattr(tag, 'identifier'):
                print(f"UID: {Fore.CYAN}{tag.identifier.hex().upper()}{Style.RESET_ALL}")

            # For MIFARE Classic cards
            if hasattr(tag, 'product') and 'MIFARE Classic' in tag.product:
                self._crack_mifare_classic(tag)
            else:
                print(f"{Fore.YELLOW}Card cracking not supported for this card type.{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"Error analyzing card: {e}")

    def _crack_mifare_classic(self, tag):
        """Attempt to crack a MIFARE Classic card"""
        print(f"\n{Fore.GREEN}=== MIFARE Classic Cracking ==={Style.RESET_ALL}")

        # Get the number of sectors
        num_sectors = 16  # Default for MIFARE Classic 1K
        if hasattr(tag, 'size'):
            if tag.size > 1024:
                num_sectors = 40  # MIFARE Classic 4K

        print(f"Card has {Fore.CYAN}{num_sectors}{Style.RESET_ALL} sectors")

        # Try to read each sector with known keys
        for sector in range(num_sectors):
            print(f"\n{Fore.BLUE}Sector {sector}:{Style.RESET_ALL}")
            sector_cracked = False

            # Try authentication with known keys
            for key_type in ['A', 'B']:
                for key in tqdm(self.known_keys, desc=f"Trying Key {key_type}", leave=False):
                    try:
                        # Authenticate with the key
                        if tag.authenticate(sector, key, key_type == 'A'):
                            print(f"{Fore.GREEN}Key {key_type} found: {key.hex().upper()}{Style.RESET_ALL}")

                            # Try to read the sector data
                            try:
                                data = tag.read(sector * 4)
                                print(f"Data: {data.hex()}")
                                sector_cracked = True
                                break
                            except Exception as e:
                                print(f"Authentication succeeded but read failed: {e}")
                    except Exception:
                        continue

                if sector_cracked:
                    break

            if not sector_cracked:
                print(f"{Fore.RED}Failed to crack sector {sector}{Style.RESET_ALL}")

    def run(self):
        """Run the NFC cracker"""
        print(f"\n{Fore.GREEN}=== NFC Cracker Tool ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}Initializing...{Style.RESET_ALL}")

        if not self.connect():
            print(f"{Fore.RED}Failed to connect to NFC reader. Exiting.{Style.RESET_ALL}")
            return

        try:
            while True:
                print(f"\n{Fore.CYAN}Waiting for NFC card...{Style.RESET_ALL}")
                target = self.scan_for_targets()

                if target:
                    self.analyze_card(target)

                    if not self.args.continuous:
                        break

                if not self.args.continuous:
                    break

                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
        finally:
            if self.device:
                self.device.close()

def main():
    parser = argparse.ArgumentParser(description='NFC Card Cracker Tool')
    parser.add_argument('-k', '--key-file', help='File containing known keys (hex format, one per line)')
    parser.add_argument('-c', '--continuous', action='store_true', help='Continuously scan for cards')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-s', '--simulation', action='store_true', help='Run in simulation mode (no hardware required)')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    cracker = NFCCracker(args)
    cracker.run()

if __name__ == "__main__":
    main()