#!/bin/sh
#SBATCH -J beast_run                         # Job name
#SBATCH --partition=common                   # Use the common partition
#SBATCH --qos=normal                         # Use the normal queue
#SBATCH --mail-type=END,FAIL                 # Email notifications
#SBATCH --mail-user=cduitama@pasteur.fr      # Your email address
#SBATCH --mem=10G                            # Fixed memory allocation
#SBATCH --nodelist=maestro-1007              # Request specific node
#SBATCH --gres=disk:50000                    # Reserve 50 GB of local disk space
#SBATCH -D ./                                # Initial directory

# Load necessary modules
module load beagle-lib/4.0.1                 # Load BEAGLE library
module load graalvm/ce-java19-22.3.1         # Java environment compatible with BEAST
module load beast/v2.7.3                     # Load BEAST2 module

# Set temporary directory
export TMPDIR=/pasteur/appa/scratch/cduitama/tmp

# Parse the number of threads from command line argument
# Default to 1 if not provided
threads=${1:-1}

# Manually handle CPU allocation since you are not using srun
# SLURM_CPUS_PER_TASK defined as part of submission command
export SLURM_CPUS_PER_TASK=$threads

# Create the output directory based on the number of threads
output_dir="${threads}_threads"
mkdir -p $output_dir

# Use the SLURM_JOB_ID and current timestamp to guarantee unique filenames
timestamp=$(date +%s)
job_id=${SLURM_JOB_ID:-unknown}

# Define the combined log file path
log_file="${output_dir}/beast_run_${threads}_${job_id}_${timestamp}.log"

echo $threads

# Run BEAST using BEAGLE with SSE and specified number of threads
beast -beagle -threads $threads -beagle_SSE -beagle_CPU /pasteur/zeus/projets/p02/DEMI_clocks/cduitama/BEAST_performance/partitioned_example.xml > $log_file 2>&1

# After execution, record detailed SLURM statistics
sacct -j $SLURM_JOB_ID --format=JobID,JobName%30,Partition,NodeList%30,State,ExitCode,Elapsed,CPUTime,UserCPU,SystemCPU,TotalCPU,MaxRSS,MaxVMSize,MaxDiskRead,MaxDiskWrite,AveRSS,AveVMSize,AveDiskRead,AveDiskWrite,AllocCPUS,NTasks,NNodes,Submit,Start,End > "${output_dir}/slurm_usage_${threads}_${job_id}_${timestamp}.txt"