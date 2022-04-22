# Commands to create the singularity image for AlphaFold

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
```docker
Bootstrap: docker
From: nvidia/cuda:11.1.1-cudnn8-runtime-ubuntu20.04

%setup
#section are first executed on the host system outside of the container after the base OS has been installed. . You can reference the container file system with the $SINGULARITY_ROOTFS environment variable in the %setup section


%files
#The %files section allows you to copy files into the container with greater safety than using the %setup section. Its general form is
#Useless for now.

%environment
  #Define environment variable that will be executed at each runtime.
  export TF_FORCE_UNIFIED_MEMORY="1"
  export XLA_PYTHON_CLIENT_MEM_FRACTION="4.0"
  export OPENMM_CPU_THREADS=8
  export CUDA=11.1
  export PATH=/opt/mmseqs/bin/:$PATH

  #PATH
  export PATH=/usr/local/cuda-11.1/bin:$PATH
  export LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64:$LD_LIBRARY_PATH
  export PATH=/opt/conda/bin:$PATH
  export XDG_CACHE_HOME=/opt/cache
  export COLABFOLDDIR=/opt/conda/lib/python3.7/site-packages/colabfold


%post -c /bin/bash

  #Redefine the variables
  export CUDA=11.1
  export XDG_CACHE_HOME=/opt/cache
  export COLABFOLDDIR=/opt/conda/lib/python3.7/site-packages/colabfold


  #Install necessary packages
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        cmake \
        cuda-command-line-tools-${CUDA/./-} \
        git \
        hmmer \
        kalign \
        tzdata \
        wget \
        vim \
        git \
        libfontconfig1-dev \
        libfreetype6-dev \
        libfreetype6
  rm -Rf /var/lib/apt/lists/*

  #Install hhsuite
  git clone --branch v3.3.0 https://github.com/soedinglab/hh-suite.git /tmp/hh-suite \
      && mkdir /tmp/hh-suite/build \
      && pushd /tmp/hh-suite/build \
      && cmake -DCMAKE_INSTALL_PREFIX=/opt/hhsuite .. \
      && make -j 4 && make install \
      && ln -s /opt/hhsuite/bin/* /usr/bin \
      && popd \
      && rm -rf /tmp/hh-suite

  #Install MMSEQS
  (cd  /opt;
  wget https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz;
   tar xvfz mmseqs-linux-avx2.tar.gz;
    rm mmseqs-linux-avx2.tar.gz)
  
  export PATH=/opt/mmseqs/bin/:$PATH



  # Install Miniconda package manager.
  wget -q -P /tmp \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
      && bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda \
      && rm /tmp/Miniconda3-latest-Linux-x86_64.sh

  #Add conda in the PATH.
  export PATH=/opt/conda/bin:$PATH


  #Install necessary soft with conda.
  conda update -qy conda \
      && conda install -y -c conda-forge \
        openmm=7.5.1 \
        cudatoolkit==${CUDA_VERSION} \
        pdbfixer \
        pip \
        python=3.7

  #Install alignment tools.
  conda install -c conda-forge -c bioconda kalign3=3.2.2 hhsuite=3.3.0 -y

  
  #Install ColabFold and Jaxlib
  pip3 install "colabfold[alphafold] @ git+https://github.com/sokrypton/ColabFold"
  pip3 install https://storage.googleapis.com/jax-releases/cuda111/jaxlib-0.1.72+cuda111-cp37-none-manylinux2010_x86_64.whl
  pip3 install jax==0.2.25


  #Apply patches and parameters
  cd $COLABFOLDDIR
  sed -i -e "s#props_path = \"stereo_chemical_props.txt\"#props_path = \"${COLABFOLDDIR}/stereo_chemical_props.txt\"#" batch.py
  wget -q https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt
  wget https://raw.githubusercontent.com/deepmind/alphafold/main/docker/openmm.patch
  (cd  /opt/conda/lib/python3.7/site-packages; patch -s -p0 < openmm.patch)
  rm openmm.patch

%labels
  author thibault Tubiana

%help
  Singularity for running colabfold localy. 
  NOTE :
   - databases like Uniref30 or other are too big to be place in the containers. Therefore your need to download them and place them outside (check https://colabfold.mmseqs.com). Give this folder later to the picture (see usage).
   - alphafold paramerters are downloaded outsite the container as well. You will need to give a specific folder for that as well.
  
  USAGE:
   1. Define location folder of 
      - MMSEQS: bin folder of MMSEQS
      - DATABASES: Root folder that the database (should have "uniref30" inside etc..)
      - FASTA_DIR: folder that will contain the fasta file
      - PARAMS_DIR: fodler that will contain Alphafold Cache File, correspond to XDG_CACHE_HOME
      - MSA_DIR: Folder that will contain the multiple sequence alignment file
      - PRED_DIR: Folder that will contain the predictions
      - IMAGESINGULAIRTY: alias for the singularity container location.

   2. You can setup a shortcut for the singularity container with:
      SINGULARITYCOMAND="singularity exec \
    -B ${MMSEQS}:/programs\
    -B ${DATABASES}:/alpha/database\
    -B ${FASTA_DIR}:/inout/fasta\
    -B ${PARAMS_DIR}:/opt/cache\
    -B ${MSA_DIR}:/inout/msas -B ${PRED_DIR}:/inout/predictions --nv ${IMAGESINGULARITY}"

  3. Run colabfold_batch and colabfold_search with command like :
  CUDA_VISIBLE_DEVICES=0 $SINGULARITYCOMAND colabfold_batch --model-type /inout/msas /inout/predictions
```