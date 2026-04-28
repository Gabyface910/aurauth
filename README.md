## How to use Aurauth
Aurauth is cross-platform and entirely Python!
Just run `python3 aurauth/main.py` and you'll be ready to go!
### Importing a QR code
When a website asks to set up your 2FA, take a screenshot of the QR code. Open Aurauth and click "Import QR Screenshot". Choose the QR code image and off you go! Aurauth will supply your 2FA codes now.
### Deleting an account from Aurauth
To delete an account from Aurauth, delete a portion of the secrets.json file. An example of a portion would be this:
```json
{
    "Website Name": {
        "secret": "SIX7BHI67BJY67 (this is NOT my secret; it is an example)",
        "user": "You"
    }
}
```
Delete **ONLY** that portion of secrets.json. If you mess it up, Aurauth will stop working. Always download your 2FA recovery codes.

## Why choose Aurauth?
Aurauth is entirely local and sends NO DATA back to Gabyface910. Aurauth is also modular. If you need your codes on a different PC, you can take `aurauth/secrets.json` with you! It will work no matter where you are. Feel free to investigate the code! It's literally one file!

## Prerequisites
Python 3 (newest version)
#### Python Libraries
pyotp
pathlib
pillow
pyzbar
