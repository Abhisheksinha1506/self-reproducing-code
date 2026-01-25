import os
import subprocess
import datetime
import hashlib

def evolve():
    base_dir = os.path.dirname(__file__)
    quine_path = os.path.join(base_dir, 'quine.py')
    log_path = os.path.join(base_dir, 'evolution.log')

    if not os.path.exists(quine_path):
        # Initial robust quine
        initial_quine = "s='s=%%s;m=%%s;print(s%%(repr(s),repr(m)))';m='init';print(s%%(repr(s),repr(m)))"
        with open(quine_path, 'w') as f:
            f.write(initial_quine)

    with open(quine_path, 'r') as f:
        source = f.read().strip()

    date_str = datetime.date.today().isoformat()
    h = hashlib.md5(date_str.encode()).hexdigest()[:6]
    new_tag = f"{date_str}-{h}"

    # Mutation: update the variable 'm' in the quine
    # Expected structure: s='...';m='...';print(...)
    if "';m='" in source:
        parts = source.split("';m='")
        prefix = parts[0] + "';m='"
        suffix_parts = parts[1].split("';print")
        suffix = "';print" + suffix_parts[1]
        new_source = f"{prefix}{new_tag}{suffix}"
    else:
        # If it's the old quine, replace it with the new structure
        new_source = f"s='s=%%s;m=%%s;print(s%%(repr(s),repr(m)))';m='{new_tag}';print(s%%(repr(s),repr(m)))"

    # Verify quine property
    temp_quine = os.path.join(base_dir, 'temp_quine.py')
    with open(temp_quine, 'w') as f:
        f.write(new_source)
    
    try:
        # We need to use -c to run the string or just execute the file
        result = subprocess.run(['python3', temp_quine], capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if output == new_source:
            # Success!
            with open(quine_path, 'w') as f:
                f.write(new_source)
            status = "SUCCESS"
            mutation_desc = f"Updated m to {new_tag}"
        else:
            status = "FAILED"
            status += f" (Out len: {len(output)}, Src len: {len(new_source)})"
            mutation_desc = f"Quine property broken. Stderr: {stderr[:50]}... Output starts with: {output[:30]}..."
            
    except Exception as e:
        status = "ERROR"
        mutation_desc = str(e)
    finally:
        if os.path.exists(temp_quine):
            os.remove(temp_quine)

    # Log results
    with open(log_path, 'a') as f:
        f.write(f"| {date_str} | {status} | {mutation_desc} |\n")

if __name__ == "__main__":
    evolve()
