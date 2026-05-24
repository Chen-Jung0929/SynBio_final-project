#!/usr/bin/env python3
"""
NCHC Slurm Script Compliance Validator
Checks any sbatch script to ensure it strictly respects NCHC Taiwania 3 partition resources.
Usage:
    python validate_slurm.py <path_to_slurm_script.sh>
"""

import sys
import re
import json
from pathlib import Path

RULES_PATH = Path(__file__).parent / "nchc_slurm_rules.json"

def load_rules():
    if not RULES_PATH.exists():
        print(f"[-] Rules configuration not found at {RULES_PATH}")
        sys.exit(1)
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_slurm_script(script_path):
    """
    Parses a slurm script and extracts #SBATCH directives.
    Returns a dict of configuration.
    """
    config = {
        "partition": None,
        "mem": None,
        "cores": None,
        "nodes": None,
        "tasks": None,
        "gres": None,
        "account": None
    }
    
    with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("#SBATCH"):
                continue
            
            # Remove #SBATCH prefix and strip whitespace
            body = line[8:].strip()
            
            # Matches options like -p partition or --partition=partition
            part_match = re.search(r'(?:(?:^|\s)-p\b|--partition=)\s*([^\s]+)', body)
            if part_match:
                config["partition"] = part_match.group(1)
                
            mem_match = re.search(r'(?:--mem=)\s*([^\s]+)', body)
            if mem_match:
                config["mem"] = mem_match.group(1)
                
            cores_match = re.search(r'(?:(?:^|\s)-c\b|--cpus-per-task=)\s*([0-9]+)', body)
            if cores_match:
                config["cores"] = int(cores_match.group(1))
                
            nodes_match = re.search(r'(?:(?:^|\s)-N\b|--nodes=)\s*([0-9]+)', body)
            if nodes_match:
                config["nodes"] = int(nodes_match.group(1))
                
            tasks_match = re.search(r'(?:(?:^|\s)-n\b|--ntasks=)\s*([0-9]+)', body)
            if tasks_match:
                config["tasks"] = int(tasks_match.group(1))
                
            gres_match = re.search(r'(?:--gres=)\s*([^\s]+)', body)
            if gres_match:
                config["gres"] = gres_match.group(1)
                
            account_match = re.search(r'(?:(?:^|\s)-A\b|--account=)\s*([^\s]+)', body)
            if account_match:
                config["account"] = account_match.group(1)
                
    return config

def validate_config(config, rules):
    partition_name = config.get("partition")
    if not partition_name:
        return False, ["Missing #SBATCH -p or --partition directive!"]
    
    # Try case-insensitive matching for convenience, but NCHC is case sensitive
    partition_rules = None
    for name, r in rules["partitions"].items():
        if name.lower() == partition_name.lower():
            partition_rules = r
            # Use official case
            partition_name = name
            break
            
    if not partition_rules:
        return False, [f"Unknown NCHC partition '{partition_name}'. Please verify the spelling."]
    
    errors = []
    
    # Check Account/Project Name
    if not config.get("account"):
        errors.append("WARNING: Missing #SBATCH -A or --account directive. You must specify your NCHC project ID (e.g. MST109178).")
        
    # Check special multi-node rules (e.g., ngs224core, ngs448core)
    if "cores_per_node" in partition_rules:
        expected_nodes = partition_rules["nodes"]
        expected_cores = partition_rules["cores_per_node"]
        
        if config.get("cores") != expected_cores:
            errors.append(f"Partition {partition_name} requires exactly -c {expected_cores} (cpus-per-task)!")
        if config.get("tasks") != expected_nodes:
            errors.append(f"Partition {partition_name} requires exactly -n {expected_nodes} (ntasks)!")
        if config.get("mem"):
            errors.append(f"Partition {partition_name} does NOT require a --mem parameter. Please remove --mem.")
            
        return len(errors) == 0, errors
        
    # Check regular nodes mem and core specifications
    expected_cores = partition_rules["cores"]
    expected_mem_gb = partition_rules["mem_gb"]
    
    # Validate Core count
    if config.get("cores") != expected_cores:
        errors.append(f"Core count mismatch for {partition_name}! Expected -c {expected_cores}, found -c {config.get('cores')}")
        
    # Validate Memory format & size
    mem_val = config.get("mem")
    if not mem_val:
        errors.append(f"Missing --mem parameter! Partition {partition_name} requires strictly --mem={expected_mem_gb}g")
    else:
        # Match value and unit (e.g., 53g or 53G or 53GB)
        mem_match = re.match(r'([0-9]+)\s*([gGmM])', mem_val)
        if not mem_match:
            errors.append(f"Invalid memory format '{mem_val}'! Use e.g. --mem={expected_mem_gb}g")
        else:
            val = int(mem_match.group(1))
            unit = mem_match.group(2).lower()
            
            # Normalize to GB
            if unit == 'm':
                val = val / 1024
                
            if int(val) != expected_mem_gb:
                errors.append(f"Memory size mismatch for {partition_name}! Expected --mem={expected_mem_gb}g, found --mem={mem_val}")
                
    # Validate GPU configurations
    expected_gpus = partition_rules["gpus"]
    gres_val = config.get("gres")
    
    if expected_gpus > 0:
        if not gres_val:
            errors.append(f"Missing GPU resource specification! Partition {partition_name} requires --gres=gpu:{expected_gpus}")
        else:
            # Parse gres (e.g. gpu:2)
            gres_match = re.search(r'gpu:([0-9]+)', gres_val)
            if not gres_match:
                errors.append(f"Invalid --gres format '{gres_val}'. Expected --gres=gpu:{expected_gpus}")
            else:
                gpus = int(gres_match.group(1))
                if gpus != expected_gpus:
                    errors.append(f"GPU count mismatch! Partition {partition_name} requires --gres=gpu:{expected_gpus}, found {gres_val}")
    elif gres_val and "gpu" in gres_val:
        errors.append(f"CPU Partition {partition_name} should NOT specify GPU resources (--gres)!")
        
    return len(errors) == 0, errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_slurm.py <path_to_slurm_script.sh>")
        sys.exit(1)
        
    script_path = Path(sys.argv[1])
    if not script_path.exists():
        print(f"[-] Script not found: {script_path}")
        sys.exit(1)
        
    rules = load_rules()
    config = parse_slurm_script(script_path)
    
    print(f"[*] Validating Slurm script: {script_path.name}")
    print(f"[*] Parsed Config: {json.dumps(config, indent=2)}")
    print("-" * 50)
    
    success, errors = validate_config(config, rules)
    if success:
        print("[+] SUCCESS: Script is fully compliant with NCHC Taiwania 3 partition rules!")
        if errors: # Warnings
            for w in errors:
                print(f"[!] {w}")
        sys.exit(0)
    else:
        print("[-] COMPLIANCE ERROR: Script violates NCHC resource constraints:")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
