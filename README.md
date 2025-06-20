# NFC Cracker

A Python-based tool for analyzing and cracking NFC cards, particularly MIFARE Classic and Ultralight cards.

## Disclaimer

This tool is provided for educational and research purposes only. Use it only on cards that you own or have explicit permission to test. Unauthorized access to NFC cards may be illegal in your jurisdiction.

## Features

- Detect and identify various types of NFC cards
- Read data from NFC cards
- Crack MIFARE Classic cards using various attack methods:
  - Nested authentication attack
  - Darkside attack
  - MFOC (MIFARE Classic Offline Cracker) attack
- Read and analyze MIFARE Ultralight cards
- Attempt authentication bypass on MIFARE Ultralight C cards
- Dump and save card contents
- Analyze card data for common patterns

## Requirements

- Python 3.6 or higher
- NFC reader compatible with nfcpy (e.g., ACR122U, Sony RC-S380)
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Connect your NFC reader to your computer

## Usage

### Basic NFC Card Analysis

To analyze an NFC card and attempt to crack it if it's a MIFARE Classic:

```bash
python nfc_cracker.py
```

### Advanced Attacks

For more specific attacks, use the advanced_attacks.py script:

```bash
# Perform a nested attack
python advanced_attacks.py --attack nested --sector 1 --known-sector 0

# Perform a darkside attack
python advanced_attacks.py --attack darkside

# Perform an MFOC attack (combines multiple techniques)
python advanced_attacks.py --attack mfoc

# Read and analyze a MIFARE Ultralight card
python advanced_attacks.py --attack ultralight
```

### Command-line Options

#### nfc_cracker.py

- `-k, --key-file FILE`: Specify a file containing known keys (hex format, one per line)
- `-c, --continuous`: Continuously scan for cards
- `-v, --verbose`: Enable verbose output

#### advanced_attacks.py

- `-a, --attack {nested,darkside,mfoc,ultralight}`: Specify the attack type
- `-s, --sector N`: Target sector for nested attack (default: 0)
- `-k, --known-sector N`: Known sector with known key for nested attack (default: 0)
- `-v, --verbose`: Enable verbose output

## Supported Cards

- MIFARE Classic (1K, 4K)
- MIFARE Ultralight
- MIFARE Ultralight C
- MIFARE DESFire (limited functionality)
- FeliCa (limited functionality)

## Known Keys

The tool comes with a set of default keys that are commonly used in MIFARE Classic cards. You can add your own keys by creating a text file with one key per line (in hexadecimal format) and using the `--key-file` option.

Example key file:
```
FFFFFFFFFFFF
000000000000
A0A1A2A3A4A5
B0B1B2B3B4B5
```

## Troubleshooting

### NFC Reader Not Found

If the tool cannot find your NFC reader, make sure:
1. The reader is properly connected
2. You have the necessary drivers installed
3. You have the required permissions to access the device

On Linux, you may need to add udev rules to allow non-root access to the NFC reader.

### Card Not Detected

If the tool cannot detect your card:
1. Make sure the card is properly positioned on the reader
2. Try moving the card slightly
3. Check if the card is supported by the tool

## License

This project is licensed under the MIT License - see the LICENSE file for details.
