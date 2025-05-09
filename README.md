# OCR_Datalogview
Read OCR and keep data in .log

# 📷 OCR Warning Capture System for Jetson Nano

This program performs OCR on images captured from a machine monitor screen via a signal splitter.  
Running on a **Jetson Nano**, it continuously monitors for **warning signals** using **OpenCV** edge detection and template matching.

When a match is detected:
1. It **captures the screen**.
2. **Separates each line** using a predefined recipe.
3. Performs **OCR** on the extracted lines using **Tesseract**.
4. **Logs** the results to a `.log` file.
5. **Uploads** the data to a web server.

> ⚙️ Ideal for industrial or embedded systems that require automated screen monitoring and real-time alert logging.

---

## 🛠 Installation Guide

### 1. Update System
```sudo apt-get update```
### 2. Set Up Swap File (4GB)
```
free -h
sudo fallocate -l 4G /var/swapfile
sudo chmod 600 /var/swapfile
sudo mkswap /var/swapfile
sudo swapon /var/swapfile
sudo bash -c 'echo "/var/swapfile swap swap defaults 0 0" >> /etc/fstab'
sudo reboot
```
### 3. Install Utilities
```
sudo apt install net-tools
sudo apt install nano
sudo apt install htop
```
To run `htop:`
```htop```
### 4. Install SSH Server
```
sudo apt update
sudo apt install openssh-server
sudo ufw allow ssh
```
### 5. Install Tesseract OCR
```
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```
### 6. Install Python & Libraries
```
sudo apt install python3-pip
pip3 install --upgrade pip setuptools wheel
pip3 install cmake scikit-build
pip3 install pytesseract
pip3 install -r requirements.txt
```
> ⚠️ **Note:** Do **not** install `opencv-python` via `pip` on Jetson Nano, as it may not support hardware acceleration.
### 7. Install OpenCV (> 4.5) on Jetson Nano

Follow the official guide from Qengineering:  
🔗 [Install OpenCV on Jetson Nano](https://qengineering.eu/install-opencv-on-jetson-nano.html)

> ✅ This ensures OpenCV is optimized for Jetson Nano with CUDA support.
---
### 8. Install Visual Studio Code
**For Jetson Nano:**
```
git clone https://github.com/JetsonHacksNano/installVSCode.git
cd installVSCode
./installVSCode.sh
```
**For Raspberry Pi:**
```
sudo apt install ./code_1.59.1-1629374148_arm64.deb
```
### 9. Install uhubctl (USB Power Control)
```
git clone https://github.com/mvp/uhubctl
cd uhubctl
make
sudo make install
```
#### 🧪 Test Commands
**For Raspberry Pi:**
```
sudo uhubctl -l 2 -a 0
```
**For Jetson Nano:**
```
sudo uhubctl -l 2-1 -a 2
```
### 10. Enable VNC Server on Jetson Nano
```
mkdir -p ~/.config/autostart
cp /usr/share/applications/vino-server.desktop ~/.config/autostart/.
cd /usr/lib/systemd/user/graphical-session.target.wants
sudo ln -s ../vino-server.service ./.

gsettings set org.gnome.Vino prompt-enabled false
gsettings set org.gnome.Vino require-encryption false
gsettings set org.gnome.Vino authentication-methods "['vnc']"
gsettings set org.gnome.Vino vnc-password $(echo -n 'vpd'|base64)

sudo reboot
```
---

### ⏰ Setup Crontab for Auto-Start and Scheduling

To ensure your scripts run automatically at boot and on a schedule, set up a **crontab** as follows:

1. Open the crontab editor (replace `yourusername` with your actual username):
```
sudo crontab -e -u yourusername
```
2. Delete all existing content and replace it with the following:
   
**Device**
```
# m h  dom mon dow   command
@reboot sleep 60 && /usr/bin/python3 /home/vpd/MoldDataLogviewJetson/VPDDatalog/oled_module.py >> /home/vpd/Desktop/log_oled.log 2>&1
@reboot sleep 60 && OPENBLAS_CORETYPE=ARMV8 /usr/bin/python3 /home/vpd/MoldDataLogviewJetson/VPDDatalog/main.py >> /home/vpd/Desktop/log_main.log 2>&1
15 0 * * * /usr/bin/python3 /home/vpd/MoldDataLogviewJetson/VPDDatalog/autoupload.py
#@reboot sleep 10 && xrandr --fb 1600x900
@reboot sleep 20 && /usr/bin/python3 /home/vpd/MoldDataLogviewJetson/getDatetime/updatetime.py
@reboot sleep 60 && OPENBLAS_CORETYPE=ARMV8 /usr/bin/python3 /home/vpd/MoldDataLogviewJetson/VPDDatalog/main.py >> /home/vpd/Desktop/log_main.log 2>&1
```
**Server**
```
# m h  dom mon dow   command
#@reboot sleep 60 && /usr/bin/python3 /etc/cmd.py
#@reboot mkdir Desktop/12345Test
#@reboot echo hello > Desktop/hello
@reboot sleep 30 && /usr/bin/bash /etc/init.d/mqbroker.sh
#@reboot sleep 60 && echo hello > Desktop/hello
@reboot sleep 40 && /usr/bin/python3 configdatabase/main.py >> /home/vpd01/Desktop/log_main.log 2>&1
@reboot sleep 20 && /usr/bin/python3 configdatabase/updatetimepi.py
1 0 * * * /usr/bin/python3 configdatabase/pubdata.py
```
### 📘 Explanation
- `@reboot`: Run the script once after every system reboot.
- `sleep X`: Delays execution by X seconds to allow other services to start first.
- `>> file.log 2>&1`: Appends both output and errors to a log file.
- `35 1 * * *`: Runs `autoupload.py` every day at 01:35 AM.
- `15 0 * * *`: Runs daily at 00:15 (12:15 AM).
- `OPENBLAS_CORETYPE=ARMV8`: Ensures better performance for OpenCV/Tensor libraries on ARM architecture.

> ✅ This setup ensures your OCR and display modules start automatically, and data uploads happen daily without manual intervention.

---

### 🖥️ How to Disable or Enable GUI on Boot (Ubuntu 20.04)

#### 🚫 Disable GUI on Boot
To boot into command-line mode (multi-user target), run:

```
sudo systemctl set-default multi-user
gnome-session-quit
```
> This will stop launching the graphical desktop environment after reboot.

#### ✅ Enable GUI on Boot
To restore the graphical interface on startup:
```
sudo systemctl set-default graphical
sudo systemctl start gdm3
```
> `gdm3` is the GNOME Display Manager. If you're using another display manager (e.g., `lightdm`), replace `gdm3` accordingly.
