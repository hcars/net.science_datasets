#!/bin/bash
#SBATCH --job-name=aw
#SBATCH --nodes=1
#SBATCH --time=48:00:00
#SBATCH --output=job_output/%j-out
#SBATCH -p bii
module load anaconda
source activate network_crawler
python trade_data_cleaner.py
