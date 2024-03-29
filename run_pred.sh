#!/usr/bin/env bash


# 1. ===== PARAMETER SETINGS <- NEED TO BE MODIFY AT EVERYRUN ========
JOBNAME="CHANGEME"  #<--- name of the the fasta file, WITHOUT the extension
FASTA_DIR=`pwd` #DIRECTORY OF THE FASTA FILE

#  Default Options. Change it if you want :-) 
MODELTYPE="auto" #COULD BE AlphaFold2-multimer-v1, AlphaFold2-multimer-v2, AlphaFold2-ptm, auto
MINIMISATION="--amber --use-gpu-relax" # COMMENT To remove minimisation
NMER=1 #Number of MERS, 2 for DIMERS (symetrical), 3 for Trimers..... /!\ IT IS DIFFERENT FROM MULTIMERS WITH 2 SEQUENCES SEPARATED BY ':'
NUMRECYCLE=3 #Number of recycling of each model. should be 3 at minimum to improve a bit models.

DBLOADMODE=3 #3 = faster reading but do not take advantage of cached files. 2 is faster when the databse is already in the memory.
USEENV=1 # 0 = do not use environmental database, 1=Use environmentale databse. 

DOALIGNMENT=true # Comment or set to false if you already have a folder called "msas" with an a3m MSA inside.
DOMODELS=true # Comment or set to false if you don't want to make the models (only generate MSAS)
GPUINDEX=0 #For multiGPU nodes, select only the GPU 0. Change to your favourite GPU number!

# 2. ===== other parameters, don't change if except if you know what you are doing :-) 
FASTA_FILE=${JOBNAME}.fasta #FASTA NAME
MSA_DIR=${FASTA_DIR}/msas #FOLDER THAT WILL CONTAIN THE MSA
PRED_DIR=${FASTA_DIR}/predictions #FOLDER THAT WILL CONTAIN PREDICTIONS
PARAMS_DIR=/mnt/DATASPEED/alphafold/params
DATABASES=/mnt/DATASPEED/alphafold/database
IMAGESINGULARITY=/mnt/DATASPEED/alphafold/container/colabfold_current.sif #LOCATION OF THE SINGULARITY IMAGE

# 3. ==== Creation of the output dir in the $FASTA_DIR
mkdir -p ${FASTA_DIR} &> /dev/null
mkdir -p ${MSA_DIR} &> /dev/null
mkdir -p ${PRED_DIR} &> /dev/null



# 4. ==== PREPARATION OF THE SINGULARITY COMMAND
#     Note :  -B are mounting point to link folder on the host machine to the singularity container.
SINGULARITYCOMAND="singularity exec \
 -B ${DATABASES}:/alpha/database\
 -B ${FASTA_DIR}:/inout/fasta\
 -B ${PARAMS_DIR}:/opt/cache\
 --env XLA_PYTHON_CLIENT_MEM_FRACTION=4.0 \
 --env TF_FORCE_UNIFIED_MEMORY=1\
 --env XLA_PYTHON_CLIENT_PREALLOCATE=false\
 --env TF_FORCE_GPU_ALLOW_GROWTH=true\
 -B ${MSA_DIR}:/inout/msas -B ${PRED_DIR}:/inout/predictions --nv ${IMAGESINGULARITY}"


cd $FASTA_DIR


if [ "$DOALIGNMENT" == true ]; then
  echo "-- Doing alignment with MMSEQS --"
  touch searchingSequences
   $SINGULARITYCOMAND\
  	    colabfold_search -s 8 \
  	    --db1 uniref30_2103_db \
        --db3 colabfold_envdb_202108_db \
  	    --use-env $USEENV \
  	    --use-templates 0 \
  	    --filter 1 \
  	    --expand-eval inf \
  	    --align-eval 10 \
  	    --diff 0 \
  	    --qsc -20.0 \
  	    --max-accept 10 \
  	    --db-load-mode $DBLOADMODE \
            --thread 24 \
  	    /inout/fasta/${FASTA_FILE} /alpha/database/ /inout/msas > outalign.txt 2>&1
  rm searchingSequences
  touch searchingSequencesDone
  
  cd msas
  echo "Renaming A3M files"
  for file in `ls *.a3m`; do
  filename=`python3 <<EOF
input = open("$file", 'r')
while input:
    line=input.readline()
    if line.startswith('>'):
        name=line.replace('>','').strip().split('\t')[0]
        print(name)
        break
EOF
`
  echo $filename
    mv $file "${filename}.a3m"
  done
  cd ..
fi

#Replace the models to have NMERS (per default : 1)
for file in `ls msas/*.a3m`;
  do
  echo $file
  sed -i -E "s|(#[0-9]*\t)[0-9]+|\1$NMER|g" $file
done


if [ "$DOMODELS" == true ]; then
  echo "-- Doing models --"
  touch makingModels
  CUDA_VISIBLE_DEVICES=$GPUINDEX $SINGULARITYCOMAND colabfold_batch --model-type ${MODELTYPE} $MINIMISATION --num-recycle $NUMRECYCLE /inout/msas /inout/predictions
  rm makingModels
  touch makingModelsDone
  
  cd predictions
  NSEQS=`ls -l *.a3m | wc -l` 
  #put each models into a subdirectory if there are several models made.
  if [ $NSEQS -gt 1 ]; then
    for file in `ls *.a3m`; do
      seq=`basename -s .a3m $file`
      mkdir $seq >/dev/null 2>&1
      mv $seq* $seq >/dev/null 2>&1
    done
  fi
  cd ..
fi
