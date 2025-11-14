Quick Start Guide for Raspberry Pi
==================================

This guide will help you to connect to the Raspberry Pi, set it up, and get started with your projects.

# Connecting to the Raspberry Pi

## 1. Powering Up the Raspberry Pi

1. Connect the Raspberry Pi to a power source, using a compatible power adapter, laptop USB port, etc. with a micro-USB cable.
2. (Optional) Connect an external display via HDMI, a keyboard, and a mouse for direct interaction.
3. Wait for the Raspberry Pi to boot up. This may take a minute or two.

## 2. Connecting to the Raspberry Pi via SSH
1. Open a terminal on your computer.
2. Use the SSH command to connect:
   ```bash
   ssh pi@raspberrypi.local
   ```
   The default password is `raspberry`.
3. If prompted, type `yes` to accept the SSH key fingerprint.
   
You should now be logged into the Raspberry Pi terminal.

## 3. Updating the System
It's a good idea to update the system packages to the latest versions. Run the following commands:
```bash
sudo apt update
sudo apt upgrade -y
```

## 4. Setting it Up

First, you need to install all the necessary dependencies. Run the following command:
```bash
sudo apt install -y python3 python3-pip python3-venv git
```

### Configuring Git

You must of course configure git with your name and email:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

and optionally set up SSH keys for GitHub access:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

When prompted, you can just press Enter to accept the default file location and leave the passphrase empty for convenience. Then add the SSH key to the ssh-agent:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Finally, copy the SSH key to your clipboard:

```bash
cat ~/.ssh/id_ed25519.pub
```
and add it to your GitHub account under Settings > SSH and GPG keys.

After completing these steps, you should be ready to clone repositories and push changes to GitHub from your Raspberry Pi.

## Installing uv

To install `uv`, run the following command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv --version
```

## 5. Ending the SSH Session
When you're done, you can log out of the Raspberry Pi by typing:
```bash
exit
```

# Setting Up Your Projects

In this guide, we will cover how to use `uv`, a tool for managing Python environments and packages, on your Raspberry Pi.

*This section will come later.*

