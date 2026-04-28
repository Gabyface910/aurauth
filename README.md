## How to use Aurauth
Aurauth is cross-platform and entirely Python!
Just run `python3 aurauth/main.py` and you'll be ready to go!
### Importing a QR code
When a website asks to set up your 2FA, take a screenshot of the QR code. Open Aurauth and click "Import QR Screenshot". Choose the QR code image and off you go! Aurauth will supply your 2FA codes now.

## Why choose Aurauth?
Aurauth is entirely local and sends NO DATA back to Gabyface910. Aurauth is also modular. If you need your codes on a different PC, you can take `aurauth/secrets.json` with you! It will work no matter where you are.

## Prerequisites
Python 3 (newest version)
#### Python Libraries
pyotp
pathlib
pillow
pyzbar
