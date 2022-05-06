from glob import glob
import os
import numpy as np
from pathlib import Path
import sys

print("Basic pyton script to generate pymol file for alphafold models")
print("Improvement will come late...")
print("USAGE : ")
print("  1. Go to your working directory (where you have the folder 'predictions' but do not go inside'")
print("  2. pythyon generate_pml.py")
print("  3. pymol visualisation.pml")

def keep_relax(models):
    keep = []
    for model in models:
        if "_unrelaxed" in model:
            relaxed = model.replace('_unrelaxed', "_relaxed")
            if relaxed in models :
                if relaxed not in keep:
                    keep.append(relaxed)
            else:
                keep.append("model")

    return keep

models=glob("predictions/**/*.pdb")
if len(models) == 0:
    models = glob("predictions/*.pdb")
    if len(models) == 0:
        print("no models found")
        sys.exit(0)
models = keep_relax(models)

numfolder = len(models[0].split('/'))
relaxed_or_notrelaxed = {}
cmdload = ''
rename = ''
firstname = ''
groupcmd = ""


if numfolder > 2:
    group=True
    folders=list(np.unique([x.split('/')[1] for x in models]))
    for f in folders:
        tmp = [x for x in models if f in x.split('/')[1]]
        if "_relaxed" in tmp[0]:
            relaxed_or_notrelaxed[f] = "relaxed"
            labelRelaxed = "mini"
            cmdload = cmdload+f'loadall predictions/{f}/*_relaxed*.pdb\n'
        else:
            relaxed_or_notrelaxed[f] = "unrelaxed"
            cmdload = cmdload+f'loadall predictions/{f}/*_unrelaxed*.pdb\n'
            rename = "alter chain B, chain='A'\nalter chain C, chain='B'\n"
            labelRelaxed = "noMini"
            #cmdload = cmdload+f'loadall predictions/{f}/*_relaxed*.pdb, {f}\n'
        groupcmd = groupcmd + f"group {f}, {f}_*\n"
else: 
    group = False
    cmdload = ''
    if "_relaxed" in models[0]:
        cmdload = cmdload+f'loadall predictions/*_relaxed*.pdb'
        labelRelaxed = "mini"
    else:
        cmdload = cmdload+f'loadall predictions/*_unrelaxed*.pdb'
        rename = "alter chain B, chain='A'\nalter chain C, chain='B'\n"
        labelRelaxed = "noMini"






pml = f"""
from pymol import cmd
cmd.run('http://pldserver1.biochem.queensu.ca/~rlc/work/pymol/align_all.py')

{cmdload}
{rename}

#Align on first model
align_all {Path(models[0]).stem},  b>70

{groupcmd}

as cartoon
set grid_mode, 1
set precomputed_lighting, 1
util.cnc
set opaque_background; 0
remove symbol H

spectrum b, rainbow_rev, minimum=10, maximum=90


"""

with open('visualisation.pml','w') as out:
    out.write(pml)



