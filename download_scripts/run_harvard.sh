#!/bin/bash
#SBATCH --job-name=aw
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --output=job_output/%j-out
#SBATCH -p bii
module load anaconda
source activate network_crawler
python download_harvard.py
