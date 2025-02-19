FROM archlinux:latest

RUN pacman --noconfirm -Syu && \
    pacman --noconfirm -S git base-devel go 

# Create a non-root user for using yay safely
RUN useradd -m auruser && \
    echo "auruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switch to the new user
USER auruser
WORKDIR /home/auruser

# Install yay
RUN git clone https://aur.archlinux.org/yay-bin.git /home/auruser/yay-bin && \
    cd /home/auruser/yay-bin && \
    makepkg -si --noconfirm && \
    rm -rf /home/auruser/yay-bin

# Set PATH (optional, but ensures yay is found)
ENV PATH="/home/auruser/.local/bin:$PATH"

# Install an AUR package globally
RUN yay -Sy --noconfirm intel-sde

# Switch back to root
USER root

RUN rm /var/cache/pacman/pkg/*

WORKDIR /tsl