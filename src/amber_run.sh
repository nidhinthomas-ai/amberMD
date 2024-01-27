#!/bin/bash

########################################################################################################################################

## This script prepares a solvated protein system and run MD simulations in AMBER using AMBERFF19SB force field. Protein has to 
## be cleaned and prepared for AMBER MD runs prior to initiating this pipeline. 

########################################################################################################################################

## sbatch amber_run.sh --protein protein.pdb --ligand ligand.pdb --json inputs.json --dest ./
    
##     OR
    
## sbatch amber_run.sh --protein protein.pdb --json inputs.json --dest ./

########################################################################################################################################

#SBATCH --time=24:00:00
#SBATCH --job-name=amber_md
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH -N 1 -n 4
#SBATCH --mem 16G

module load amber/22
module load openmpi
module load cuda
module load anaconda

source path_to_anaconda/etc/profile.d/conda.sh
conda activate biobb_amber

usage() { echo -e "\nThis script prepares a solvated protein system and run MD simulation in AMBER using AMBERFF19SB force field. Protein has to be cleaned and prepared for AMBER MD runs prior to initiating this pipeline. If the system has a non-standard ligand present, then --ligand flag should be used to run amberMD_Ligand.py instead of amberMD.py.\n";

          echo -e "sbatch amber_run.sh [--protein <protein.pdb>] [--ligand <ligand.pdb>] [--json <inputs.json>] [--dest <destination directory>] [--help]\n" 1>&2;

          echo -e "Example: sbatch path/to/amber_run.sh --protein protein.pdb --ligand ligand.pdb --json inputs.json --dest ./ \n";

          exit 1; 
        }

for arg in "$@"; do
  shift
  case "$arg" in
    '--help')      set -- "$@" '-h'   ;;
    '--protein')   set -- "$@" '-p'   ;;
    '--ligand')    set -- "$@" '-l'   ;;
    '--json')      set -- "$@" '-j'   ;;
    '--dest')      set -- "$@" '-d'   ;;
    *)             set -- "$@" "$arg" ;;
    
  esac
done

OPTIND=1
while getopts "hp:l:j:d:" opt
do
  case "$opt" in
    'h') usage; exit 0 ;;
    'p') protein=$OPTARG ;;
    'l') ligand=$OPTARG;;
    'j') json=$OPTARG  ;;
    'd') dest=$OPTARG  ;;
    '?') usage >&2; exit 1 ;;
  esac
done
shift $(expr $OPTIND - 1)

script_dir=$( dirname -- "$0"; )

if [[ -n ${ligand} ]]; then
    python path_to_amberMD/src/amberMD_Ligand.py --input ${protein} --ligand ${ligand} --json ${json} --dest ${dest}
else
    python path_to_amberMD/src/amberMD.py --input ${protein} --json ${json} --dest ${dest}
fi