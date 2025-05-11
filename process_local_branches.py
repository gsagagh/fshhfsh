import os
import subprocess

# Get GitHub details from environment variables
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
REPO_OWNER = os.getenv("REPO_OWNER")

# Check if environment variables are set
if not all([GITHUB_USERNAME, GITHUB_TOKEN, REPO_NAME, REPO_OWNER]):
    raise ValueError("Please set GITHUB_USERNAME, GITHUB_TOKEN, REPO_NAME, and REPO_OWNER environment variables.")

DECRYPT_SCRIPT = "st_to_lua.py"  # The decryptor script
BRANCHES_TO_SKIP = ["main", "master"]
COMMIT_MESSAGE = "Decrypt .st files to .lua"

def decrypt_st_to_lua(st_path):
    lua_path = st_path[:-3] + ".lua"
    try:
        subprocess.run(
            ["python3", DECRYPT_SCRIPT, st_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] Decryption failed for {st_path}")
        print(e.stderr.decode())
        return False

    if os.path.exists("out.lua"):
        os.rename("out.lua", lua_path)
        os.remove(st_path)
        print(f"[+] Decrypted: {st_path} -> {lua_path}")
        return True
    else:
        print(f"[!] out.lua not found after decrypting {st_path}")
        return False

def process_branch(branch):
    subprocess.run(["git", "checkout", branch], check=True)
    print(f"\n[*] Switched to branch: {branch}")
    changed = False

    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".st"):
                st_file_path = os.path.join(root, file)
                if decrypt_st_to_lua(st_file_path):
                    changed = True

    if changed:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"[✓] Changes pushed to {branch}")
    else:
        print("[=] No valid .st files decrypted in this branch.")

def main():
    result = subprocess.run(["git", "branch", "-r"], capture_output=True, text=True)
    branches = [
        line.strip().replace("origin/", "")
        for line in result.stdout.splitlines()
        if "->" not in line
    ]

    for branch in branches:
        if branch in BRANCHES_TO_SKIP:
            print(f"[!] Skipping branch: {branch}")
            continue
        process_branch(branch)

if __name__ == "__main__":
    main()
