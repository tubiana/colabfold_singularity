#!/bin/sh

# SETUP INSTALLDIR --> TO CHANGE
INSTALLDIR=/mnt/DATASPEED/alphafold


#Proposed filetree:
#- database (sequences databases)
#- container (list of all containers)
#- params (alphafold weights)
#- scripts (this repository basically...)


mkdir -p $INSTALLDIR/database
mkdir -p $INSTALLDIR/params
mkdir -p $INSTALLDIR/container
github clone https://github.com/tubiana/colabfold_singularity $INSTALLDIR/scripts


#1. Install Singularity 
echo "Installing Singularity"
wget https://raw.githubusercontent.com/tubiana/colabfold_singularity/main/Install_singularity.sh
sudo bash Install_singularity.sh

#2. Install Databases (can take A LOT OF TIME)
echo "Installing Databases"
cd $INSTALLDIR/database

#Install a localcopy of mmseqs to unpack the databse
wget https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz;
tar xvfz mmseqs-linux-avx2.tar.gz;
rm mmseqs-linux-avx2.tar.gz

export PATH=$INSTALLDIR/database/mmseqs/bin/:$PATH

wget https://raw.githubusercontent.com/sokrypton/ColabFold/main/setup_databases.sh
chmod +x setup_databases.sh
./setup_databases.sh database/

#Add Taxonomy
wget http://wwwuser.gwdg.de/~compbiol/colabfold/uniref30_2103_taxonomy.tar.gz
tar xzvf uniref30_2103_taxonomy.tar.gz

#3. Create the singularity container
echo "Creating Container"
today=$(date +%d%m%y)
sudo apt update 
sudo apt install fakeroot
singularity build --fakeroot colabfold_$today.sif ../scripts/colabfold_receipe.def 

ln -s colabfold_$today.sif colabfold_current.sif


#4. Replace the Running script with right folder.

cd $INSTALLDIR/scripts
sed 's|/home/alphafold|'"$INSTALLDIR"'|g' run_pred.sh > run_pred_local.sh

