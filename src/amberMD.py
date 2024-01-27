"""This script is used to run equilibrium MD simulations of protein-in-water in AMBER. 
   PDB file of the protein and a json file containing all input parameters for MD run
   are needed to perform the MD simulation. Protein.ff19SB force field is used as the
   protein force field. PMEMD.CUDA is used to perform MD simulations. The rest of the
   details can be found in the input json file format.

   Usage: python amberMD.py --input ../example/1aki.pdb --json inputs.json 
                 --dest ../example/protein-in-solution/
   
   Author: Nidhin Thomas (dr.thomas@nidhin-thomas.com) 
   
   ==================================================================================
   """

import os, sys
import argparse
from biobb_io.api.pdb import pdb
from biobb_amber.pdb4amber.pdb4amber_run import pdb4amber_run
from biobb_amber.leap.leap_gen_top import leap_gen_top
from biobb_amber.pmemd.pmemd_mdrun import pmemd_mdrun
from biobb_amber.process.process_minout import process_minout
from biobb_amber.ambpdb.amber_to_pdb import amber_to_pdb
from biobb_amber.leap.leap_solvate import leap_solvate
from biobb_amber.leap.leap_add_ions import leap_add_ions
from biobb_amber.process.process_mdout import process_mdout

import json  

def create_dictionaries(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    dictionaries = {}
    for key in data.keys():
        dictionaries[key] = data[key]
    return dictionaries

def write_mdin(parameters, output_file_path):
    ## Read the input JSON file and write it into mdin files to keep those files for reference
    with open(output_file_path, 'w') as f:
        f.write("MD: step2.in\n &cntrl\n")
        
        # Extract nested dictionary for 'mdin' if exists
        mdin_parameters = parameters.get('mdin', {})

        for key, value in mdin_parameters.items():
            if isinstance(value, str):
                f.write(f"   {key} = '{value}',\n")
            else:
                f.write(f"   {key} = {value},\n")

        f.write(" &end\n")

def prepPDB(input_PDB, forcefield, destination="./"):
        
    ## Clean the PDB file using pdb4amber tool
    output_pdb4amber_path = os.path.join(destination,'structure.pdb4amber.pdb')
    pdb4amber_run(input_pdb_path=input_PDB, output_pdb_path=output_pdb4amber_path, properties=forcefield)
    
    ## Create topology files for the protein. 
    leap_gen_top (input_pdb_path=output_pdb4amber_path,
                  output_pdb_path=os.path.join(destination,'structure.leap.pdb'), 
                  output_top_path=os.path.join(destination,'structure.leap.top'), 
                  output_crd_path=os.path.join(destination,'structure.leap.crd'), 
                  properties=forcefield)

def mdrun (stage, input_top, prop, destination="./"):

    ## PMEMD_mdrun for any steps, including Minimization, Heating, NVT, NPT, and Production
    output_traj_path = os.path.join(destination,f"pmemd.{stage}.nc")
    output_rst_path = os.path.join(destination,f"pmemd.{stage}.rst")
    output_log_path = os.path.join(destination,f"pmemd.{stage}.log")
    
    print(output_traj_path, output_rst_path, output_log_path)

    ## Create and launch bb
    pmemd_mdrun(input_top_path=os.path.join(destination,input_top["top"]),
                 input_crd_path=os.path.join(destination,input_top["crd"]),
                 input_ref_path=os.path.join(destination,input_top["crd"]),
                 output_traj_path=output_traj_path,
                 output_rst_path=output_rst_path,
                 output_log_path=output_log_path,
                 properties=prop)

def solvation (input_top, prop, destination='./'):
    
    ## Create and launch bb
    amber_to_pdb(input_top_path=os.path.join(destination,input_top["top"]),
                 input_crd_path=os.path.join(destination,input_top["crd"]),
                 output_pdb_path=os.path.join(destination,input_top["ambpdb"]),
                )

    ## Solvation of the protein
    leap_solvate(input_pdb_path=os.path.join(destination,input_top["ambpdb"]),
                 output_pdb_path=os.path.join(destination,'structure.solv.pdb'),
                 output_top_path=os.path.join(destination,'structure.solv.parmtop'),
                 output_crd_path=os.path.join(destination,'structure.solv.crd'),
                 properties=prop)

def addIons (solv_pdb, prop, destination='./'):
    
    # Create prop dict and inputs/outputs
    output_ions_pdb_path = 'structure.ions.pdb'
    output_ions_top_path = 'structure.ions.parmtop'
    output_ions_crd_path = 'structure.ions.crd'

    # Create and launch bb
    leap_add_ions(input_pdb_path=solv_pdb["pdb"],
                  output_pdb_path=os.path.join(destination, output_ions_pdb_path),
                  output_top_path=os.path.join(destination,output_ions_top_path),
                  output_crd_path=os.path.join(destination,output_ions_crd_path),
                  properties=prop)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AMBER MD pipeline for protein-in-solution.')
    parser.add_argument('-i', '--input', required=True, type=str, help='Input PDB file of the protein for MD simulation.')
    parser.add_argument('-j', '--json', required=True, type=str, help='Collection of md input parameters as a json file.')
    parser.add_argument('-o', '--dest', required=True, type=str, help='Destination directory for all outputs')
    parser.add_argument('-p', '--path', required=True, type=str, help='Path to Amber Software Installation')
    
    args = parser.parse_args()

    ## Export the amber path
    os.environ['AMBERHOME'] = 'args.path/amber/22'

    inputs_dict = create_dictionaries(args.json)

    ## PDB preparation
    prepPDB (args.input, inputs_dict["forcefield"], destination=args.dest)

    ## Minimization in vacuo
    input_min_vacuo_top = {
    "top": "structure.leap.top",
    "crd": "structure.leap.crd",
    "pdb": "structure.leap.pdb",
    }
    mdrun ("min_vacuo", input_min_vacuo_top, inputs_dict["prop_min_vacuo"], destination=args.dest)

    ##Solvation
    input_solv_top = {
    "top": "structure.leap.top",
    "crd": "structure.leap.crd",
    "pdb": "structure.leap.pdb",
    "ambpdb": "structure.ambpdb.pdb"
    }
    solvation (input_solv_top, inputs_dict["solvate_prop"], destination=args.dest)
    
    solv_pdb = {
    "pdb": "structure.solv.pdb"
    }

    ##Adding ions to the system
    addIons (solv_pdb, inputs_dict["ions_prop"], destination=args.dest)
    
    ## Minimization after solvation
    input_min_top = {
    "top": "structure.ions.parmtop",
    "crd": "structure.ions.crd",
    "pdb": "structure.ions.pdb"
    }
    mdrun ("min", input_min_top, inputs_dict["prop_min"], destination=args.dest)

    ## Heating 
    input_heat_top = {
    "top": "structure.ions.parmtop",
    "log": "pmemd.min.log",
    "rst": "pmemd.min.rst",
    "crd": "pmemd.min.rst"
    }
    mdrun ("heat", input_heat_top, inputs_dict["prop_heat"], destination=args.dest)

    ## NVT equilibration
    input_nvt_top = {
    "top": "structure.ions.parmtop",
    "log": "pmemd.heat.log",
    "rst": "pmemd.heat.rst",
    "crd": "pmemd.heat.rst"
    }
    mdrun ("nvt", input_nvt_top, inputs_dict["prop_nvt"], destination=args.dest)

    ## NPT equilibration
    input_npt_top = {
    "top": "structure.ions.parmtop",
    "log": "pmemd.nvt.log",
    "rst": "pmemd.nvt.rst",
    "crd": "pmemd.nvt.rst"
    }
    mdrun ("npt", input_npt_top, inputs_dict["prop_npt"], destination=args.dest)

    ## Production "Free" run
    input_free_top = {
    "top": "structure.ions.parmtop",
    "log": "pmemd.npt.log",
    "rst": "pmemd.npt.rst",
    "crd": "pmemd.npt.rst"
}
    mdrun ("free", input_free_top, inputs_dict["prop_free"], destination=args.dest)
