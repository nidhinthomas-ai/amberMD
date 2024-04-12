# amberMD

A python based workflow to perform MD simulations of proteins and peptides in AMBER software. 

## Introduction:

This workkflow is designed to run equilibrium MD simulations of protein-in-solution in AMBER22.0 software suite. This is a python based package that utilizes biobb_amber python package for pre-processing, simulation and post-processing. Bash scripts are used to organize the python package and run the SLURM jobs. PMEMD.CUDA extension is used to run equilibration and produciton runs. Post-processing of the MD trajectories are done using biobb_analysis and MDAnalysis packages. The user is expected to install AMBER software in order to run the simulations.

## Installation:

The dependencies should be installed prior to running the workflow. The workflow can be downloaded from GitHub.

`git clone https://github.com/nidhinthomas-ai/amberMD.git`  

The custom conda environement required for this workflow can be installed through `conda`.  

`conda env create -f environment.yml`  

In order to activate the environment:  

`conda activate biobb_amber`  

## Running end-to-end MD simulations:

End-to-end MD simulations can be performed from terminal command line interaface. For this, following command can be used. The bash script allocates necessary resources for a single equilibrium MD simulation if you want to run it in a linux cluster. The input files required for performing such MD simulations include PDB file of the protein or peptide, input arguments for the MD simulation as a .json format and optional computing resources. 

For protein-ligand complex systems:  

`sbatch amber_run.sh --protein [.pdb file of the protein] --ligand [.pdb file of the ligand] --json [.json file containing inputs parameters] --dest [destination directory] --path [path to amber software]`

For protein-only system:  

`sbatch amber_run.sh --protein [.pdb file of the protein] --json [.json file containing inputs parameters] --dest [destination directory] --path [path to amber software]`

The slurm job script amber_run.sh runs the python script with input .json file and protein data bank structure. The python script can be run using the command line interface:

`python amberMD.py --input input.pdb --json inputs.json --dest destination/directory`

`python amberMD_Ligand.py --input input.pdb --ligand ligand.pdb --json inputs.json --dest destination/directory`

The details of each parameter used in the inputs.json file is provided in inputs.md. 

## Resource Allocation:

MD simulations are computationally intensitive exercises. Therefore, users should be cautious in terms of how much resources are they using at a given time per simulation. These simulations typically require GPUs for running sufficiently large MD simulations with reasonable speed. However, oversubscribing these resources may not improve the simulation speed and eventually resulting in the wastage of resources. Therefore, it is recommended that users follow the guidelines given below for running simulations using this workflow. While MD simulations can be performed using different softwares and different configurations, it is recommended that users use the following specific set of guidelines only for amberMD workflow. 

1. For AMBER22 software suite, we recommend using one GPU for one simulation. In the SLURM script, it would be the option `#SBATCH --gres=gpu:1`
2. AMBER software would only require few computing CPU cores for running an equilibrium MD simulation and most of the computation would occur in the GPU. Therefore, we recommend using one node, ~4 CPU cores per simulation system and memory of 2GB per core. In the SLURM script, it can be set by `#SBATCH -N 1 -n 4 --mem 8G`.
3. While equilibration and production runs can be performed with PMEMD.CUDA, we recommend to use PMEMD.CPU for energy minimization. This would reduce the chance of systems crashing during energy minimization.
4. We recommend not using more than one GPU per simulation system to avoid oversubscribing resources to optimize these runs. 

## Tutorial:

There are two tutorials available for this workflow. The tutorials can be found in the example directory. In the first tutorial, a protein-in-solution is simulated. In the second tutorial, a protein-ligand complex solvated in water is simulated. Each step taken to run the simulation is described in the respective jupyter notebooks. 
