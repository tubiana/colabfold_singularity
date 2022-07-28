#!/bin/bash

#Necessary packages
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    squashfs-tools \
    libseccomp-dev \
    pkg-config\
    golang-go \
    aria2

# Download GO
export VERSION=1.13 OS=linux ARCH=amd64
wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz
sudo tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz
rm go$VERSION.$OS-$ARCH.tar.gz

# Setup GO
echo 'export GOPATH=${HOME}/go' >> ~/.bashrc 
echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc
source ~/.bashrc

#For Singularity > 3.0 DEP is required
go get -u github.com/golang/dep/cmd/dep

go get -d github.com/sylabs/singularity

export VERSION=v3.8.0 # or another tag or branch if you like 
cd $GOPATH/src/github.com/sylabs/singularity 
git fetch 
git checkout $VERSION # omit this command to install the latest 

#Compile it.
./mconfig
make -C ./builddir
sudo make -C ./builddir install
