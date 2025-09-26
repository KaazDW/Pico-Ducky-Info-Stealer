# BadUSB - System Information Exfiltration via Discord

## 📋 Description
This project implements a BadUSB tool using a Raspberry Pi Pico to exfiltrate sensitive information from a Windows computer and send it to a Discord webhook. The project includes two versions of a PowerShell script: a detailed version and a lightweight version.

## ⚠️ Warning
**This project is provided for educational and security testing purposes only.** Unauthorized use of this software to access computer systems is illegal and unethical. The author disclaims any responsibility for malicious or illegal use of this software.

## 🛠️ Required Hardware
- Raspberry Pi Pico (or Pico W)
- USB cable to connect the Pico to the target computer

## 🔧 Setting Up Raspberry Pi Pico as BadUSB
A lot of documentation is available online for setting up a Raspberry Pi Pico as a BadUSB. 
- <a href="https://www.youtube.com/watch?v=e_f9p-_JWZw&t=105s">Youtube - NetworkChuck - BadUSB</a>
- <a href="https://www.youtube.com/results?search_query=Raspberry+Pico+as+Bad+USB">Youtube - Use a Raspberry Pi Pico as a BadUSB</a>

## 📂 Project Structure

- `info_stealer_detailed.ps1`: Full version of the script that collects detailed system information
- `info_stealer_lite.ps1`: Lightweight version for faster and more discreet execution
- `payload.dd`: Command to execute to launch the PowerShell script

## 🚀 Usage

1. **Preparation**:
   - Copy your chosen PowerShell script (`info_stealer_detailed.ps1` or `info_stealer_lite.ps1`) to the Pico's USB drive
   - Rename it to `pico_computer_info_discord.ps1`
   - Create a `payloads` folder at the root of the USB drive if needed
   - Configure your Discord webhook in the PowerShell script

2. **Execution**:
   - Plug the Raspberry Pi Pico into the target computer
   - The script will run automatically and send the information to the configured Discord webhook
   - Cleans up execution traces
   
## 🔍 Features

### Detailed Version (`info_stealer_detailed.ps1`)
- BIOS information and Windows product keys
- Complete operating system details
- Hardware specifications (CPU, GPU, RAM)
- Network information (IP addresses, gateway, DNS)
- Saved Wi-Fi passwords
- Screenshot capture
- Disk space and installed updates

### Lite Version (`info_stealer_lite.ps1`)
- Essential system information
- Windows product keys
- Wi-Fi passwords
- Basic network data

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙏 Acknowledgments
This project wouldn't exist without the guidance of these examples
- [startrk1995](https://github.com/startrk1995/BadUSB)