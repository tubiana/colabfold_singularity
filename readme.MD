# Commands to create the singularity image for AlphaFold

**UPDATE:**  
You can use the script `0.insgtall_colabfold_local.sh` to install everything from scratch.
Just change the variable `$INSTALLDIR` with your location folder.

## Requirement
All the instruction are available in the syslab.io website (https://sylabs.io/guides/3.0/user-guide/installation.html#install-from-source)

1. Install all the requirement (need root access)
```sh

#Necessary packages
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    squashfs-tools \
    libseccomp-dev \
    pkg-config\
    golang-go

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
```

2. Download Singularity
```sh
go get -d github.com/sylabs/singularity
```

3. Choose your version. Singularity 3.8.0 is installed on the I2BC cluster, choose this one for more constitancy
```sh
export VERSION=v3.8.0 # or another tag or branch if you like 
cd $GOPATH/src/github.com/sylabs/singularity 
git fetch 
git checkout $VERSION # omit this command to install the latest bleeding edge code from master
```

4. Compilation
```sh
./mconfig
make -C ./builddir
sudo make -C ./builddir install
```

5. BONUS: to have autocompletion
```sh
echo 'source /usr/local/etc/bash_completion.d/singularity' >> ~/.bashrc
```

## Creation of the singularity container
*check https://singularity-tutorial.github.io/02-basic-usage/* for tutorial  
The easiest way to create the container is maybe to use a definition file. See https://sylabs.io/guides/3.5/user-guide/definition_files.html for more details.
1. Create a file with the following content (or download the one in the repository)
2. execute `sudo singularity build NAME.sif colabfold_receipe.def`
