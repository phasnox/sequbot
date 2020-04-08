echo "THIS SETUP SCRIPT IS DEPRECATED. Use docker"

DIST_NAME=$(lsb_release -a 2>/dev/null | awk '/Distributor ID/ {print $3}')
GPU_ENABLED=1

echo "Distro name: $DIST_NAME"
# Para debian
if [ $DIST_NAME = "Debian" ]; then
    echo "Installing on debian..."
    command -v sudo >/dev/null 2>&1 || { echo >&2 "sudo required but it's not installed.  Aborting."; exit 1; }
    apt-get -y purge docker.io*
    apt-get -y purge lxc-docker*
    apt-get -y update
    apt-get -y install apt-transport-https ca-certificates
    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    echo "deb https://apt.dockerproject.org/repo debian-jessie main" > /etc/apt/sources.list.d/docker.list
    apt-get -y update
    apt-cache policy docker-engine
    apt-get -y update
    apt-get -y install docker-engine
fi

# Para Ubuntu
if [ $DIST_NAME = "Ubuntu" ]; then
    echo "Installing on ubuntu..."
fi

# Para Fedora
if [ $DIST_NAME = "Fedora" ]; then
    echo "Installing on fedora..."
fi

# Para OpenSuse
if [ $DIST_NAME = "openSUSE" ]; then
    echo "Installing on openSUSE..."
fi
