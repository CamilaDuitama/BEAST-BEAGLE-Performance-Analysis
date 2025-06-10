# BEAST Performance Evaluation

This directory contains scripts, data, and logs for evaluating the performance of BEAST runs using different thread configurations on `maestro-1007`.

## Contents

- **1_threads/**: Directory for results and logs from a 1-thread BEAST run.
  - `dengue_beast_run_out.txt`: Output log.
  - `dengue_beast_run_err.txt`: Error log.
  - `slurm_usage_1.txt`: SLURM statistics.

- **2_threads/**: Directory for results and logs from a 2-thread BEAST run.
  - `dengue_beast_run_out.txt`: Output log.
  - `dengue_beast_run_err.txt`: Error log.
  - `slurm_usage_2.txt`: SLURM statistics.

- **10_threads/**: Directory for results and logs from a 10-thread BEAST run.
  - `dengue_beast_run_out.txt`: Output log.
  - `dengue_beast_run_err.txt`: Error log.
  - `slurm_usage_10.txt`: SLURM statistics.

- **beast_run.sh**: Dynamic SLURM script for running BEAST with a specified number of threads.
- **partitioned_example.xml**: Dummy dataset by Sebastian.

# How to run the script

Example for 2 threads:
```bash
sbatch --cpus-per-task=2 cpu_performance.sh 2
```
# Results

## Table of Job Metrics

| **JobID**  | **Elapsed** | **TotalCPU** | **UserCPU** | **SystemCPU** | **AllocCPUS** | **MaxRSS** | **CPU Efficiency** | **Memory Efficiency** |
|------------|-------------|--------------|-------------|---------------|---------------|------------|--------------------|-----------------------|
| 41859916   | 02:56:25    | 15:48:19     | 13:41:41    | 02:06:38      | 10            | 0.50G      | 53.76%             | 5.00%                 |
| 41860292   | 03:08:13    | 16:15:24     | 14:05:10    | 02:10:14      | 10            | 0.46G      | 51.82%             | 4.60%                 |
| 41860293   | 00:48:59    | 04:32:05     | 04:12:37    | 00:19:28      | 10            | 0.48G      | 55.55%             | 4.80%                 |
| 41860328   | 05:16:48    | 05:14:31     | 05:14:21    | 00:09:26      | 1             | 0.26G      | 99.28%             | 2.60%                 |
| 41860340   | 03:59:21    | 07:03:42     | 06:23:16    | 00:40:26      | 2             | 0.42G      | 88.51%             | 4.20%                 |


- **Elapsed Time:** Total real-world duration the job ran, from start to finish.
- **Total CPU:** Cumulative CPU time used by the job over all allocated cores.
- **User CPU:** CPU time spent executing non-kernel (user) code.
- **System CPU:** CPU time spent running kernel tasks (system-level operations).
- **Alloc CPUs:** Number of CPU cores allocated for the job.
- **MaxRSS:** Peak physical memory used by the job during execution.
- **CPU Efficiency:** Percentage of CPU time utilized relative to theoretical maximum.
- **Memory Efficiency:** Percentage of allocated memory actually used by the job.