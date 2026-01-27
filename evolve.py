from pathlib import Path
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

    # Generate human summary
    if status == "SUCCESS":
        summary = f"A new version of the quine has been born today! The code successfully mutated and passed the 'mirror test'—it can still print itself perfectly. "
        summary += f"The unique tag for this generation is {new_tag}."
    else:
        summary = f"Mutation attempt failed today. The proposed code could not reproduce itself accurately. The lineage remains unchanged to ensure survival."

    with open(os.path.join(base_dir, 'summary.txt'), 'w') as f:
        f.write(summary)

    # Update README with latest status
    readme_path = os.path.join(base_dir, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            content = f.read()
        
        start_marker = "<!-- LATEST_STATUS_START -->"
        end_marker = "<!-- LATEST_STATUS_END -->"
        
        if start_marker in content and end_marker in content:
            parts = content.split(start_marker)
            prefix = parts[0] + start_marker
            suffix = end_marker + parts[1].split(end_marker)[1]
            new_content = f"{prefix}\n> {summary}\n{suffix}"
            
            with open(readme_path, 'w') as f:
                f.write(new_content)


def update_readme(summary):
    readme_path = Path("README.md")
    if not readme_path.exists(): return
    try:
        content = readme_path.read_text()
        start = "<!-- LATEST_STATUS_START -->"
        end = "<!-- LATEST_STATUS_END -->"
        if start not in content or end not in content: return
        parts = content.split(start)
        suffix_parts = parts[1].split(end)
        prefix = parts[0] + start
        suffix = end + suffix_parts[1]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_inner = f"
*{summary} ({timestamp})*
"
        readme_path.write_text(prefix + new_inner + suffix)
    except Exception as e: print(f"⚠️ README Update Failed: {e}")
if __name__ == "__main__":
    evolve()
