# Intel RealSense + pyrealsense2 Python on Raspberry Pi 3

## Prerequisites & System Prep

- **Hardware:** Raspberry Pi 3 (4 recommended for performance)
- **OS:** Raspberry Pi OS Bullseye/Bookworm, or Ubuntu 20.04+
- **Permissions:** root (`sudo`) recommended

**Update system and install required packages:**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git cmake build-essential python3-dev python3-pip libssl-dev libusb-1.0-0-dev \
                 libgtk-3-dev libglfw3-dev pkg-config libudev-dev libxinerama-dev \
                 libxcursor-dev libusb-1.0-0 libglfw3 xvfb
```

---

## Step 1: Increase Swap (for Pi 3 RAM Limits)

```bash
sudo nano /etc/dphys-swapfile
```

Change the value to:

```
CONF_SWAPSIZE=2048
```

Exit and save (Ctrl+X, then Y, then Enter).

Apply the change:

```bash
sudo systemctl restart dphys-swapfile
```

*(Set this back to 100 after building to prevent SD card wear)*

---

## Step 2: Clone librealsense and Set Permissions

```bash
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense
./scripts/setup_udev_rules.sh
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Step 3: Build librealsense & Python Bindings

```bash
mkdir build && cd build

cmake ../ \
  -DBUILD_PYTHON_BINDINGS:bool=true \
  -DPYTHON_EXECUTABLE=$(which python3) \
  -DFORCE_LIBUVC=true \
  -DBUILD_EXAMPLES=true \
  -DBUILD_GRAPHICAL_EXAMPLES=false \
  -DCMAKE_BUILD_TYPE=Release

make -j1 # Use -j1 on Pi to avoid memory issues
sudo make install
```

**Key flags:**
- `-DBUILD_PYTHON_BINDINGS:bool=true` â€” builds pyrealsense2
- `-DFORCE_LIBUVC=true` â€” required for USB2.0/ARM
- `-DBUILD_GRAPHICAL_EXAMPLES=false` â€” disables GUI examples (saves resources on Pi 3)

*(This process takes 30+ minutes on Pi 3. Be patient.)*

---

## Step 4: Copy Python Module

Find the `.so` module:

```bash
find . -name "pyrealsense2*.so"
```

Example output:

```
./wrappers/python/pyrealsense2/pyrealsense2.cpython-311-arm-linux-gnueabihf.so
```

Copy to Python site-packages (adjust path for your Python version):

```bash
sudo cp wrappers/python/pyrealsense2/pyrealsense2*.so /usr/local/lib/python3.11/dist-packages/
```

*(Replace `python3.11` with your Python version if different, e.g., `python3.9`, `python3.10`)*

If necessary, create a directory and add `__init__.py`:

```bash
sudo mkdir -p /usr/local/lib/python3.11/dist-packages/pyrealsense2
sudo cp wrappers/python/pyrealsense2/pyrealsense2*.so /usr/local/lib/python3.11/dist-packages/pyrealsense2/
```

Create `__init__.py`:

```bash
sudo bash -c 'echo "from .pyrealsense2 import *" > /usr/local/lib/python3.11/dist-packages/pyrealsense2/__init__.py'
```

---

## Step 5: Add to PYTHONPATH (If Needed)

If module import fails, add export to your shell profile:

```bash
echo 'export PYTHONPATH=/usr/local/lib/python3.11/dist-packages:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc
```

Or for one-time use:

```bash
export PYTHONPATH=/usr/local/lib/python3.11/dist-packages:$PYTHONPATH
```

---

## Step 6: Validate the Installation

Plug in the RealSense camera via USB.

Test with Python3:

```python
import pyrealsense2 as rs
print(rs.__version__)
```

If you see a version number printed, the build succeeded!

If you see `ModuleNotFoundError`, check PYTHONPATH and the .so file location.

---

## Step 7: Cleanup and Optimization

Reduce swap size back to default to protect SD card:

```bash
sudo nano /etc/dphys-swapfile
# Change back to:
CONF_SWAPSIZE=100
sudo systemctl restart dphys-swapfile
```

Reboot if needed:

```bash
sudo reboot
```

---

## Running Your Python Script

Once pyrealsense2 is installed, your existing Python script should work as-is:

```python
import pyrealsense2 as rs

# Your original code here
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

# ... rest of your script
```

---

## Troubleshooting

### Camera Not Detected

Check USB detection:

```bash
lsusb | grep RealSense
```

If not listed, the camera may not be powered. Use an external powered USB hub.

### Module Import Error

Ensure correct Python version and path:

```bash
python3 --version
python3 -c "import sys; print(sys.path)"
```

### Permission Denied on /dev/bus/usb

Reapply udev rules:

```bash
cd ~/librealsense
./scripts/setup_udev_rules.sh
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Build Failures

- Check available disk space: `df -h`
- Increase swap further if needed
- Try disabling parallel build: `make -j1` instead of `make -j$(nproc)`

### Python Version Mismatch

If you built for Python 3.11 but use Python 3.9 at runtime, rebuild:

```bash
cd ~/librealsense/build
rm -rf *
cmake ../ -DPYTHON_EXECUTABLE=$(which python3.9) -DBUILD_PYTHON_BINDINGS:bool=true ...
make -j$(nproc)
sudo make install
```

---

## Performance Notes

- **Raspberry Pi 3:** USB 2.0 only. Expect lower frame rates and resolution than USB 3.0
- **Raspberry Pi 4:** USB 3.0. Better performance and full feature support
- **External USB Hub:** Recommended for reliable power to RealSense cameras
- **Swap Space:** Keep at default (100) after build to maximize SD card lifespan

---

## References

- IntelRealSense/librealsense: https://github.com/IntelRealSense/librealsense
- Official installation guide: https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md
- Community forums and issue tracker for troubleshooting

---

**Last updated:** November 2025

**Compatible with:** Raspberry Pi 3, Python 3.8+, librealsense 2.x