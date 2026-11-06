import os
import sys
import time
import json
import zipfile
import urllib.request

REPO = "atharva2012tiwari/vyas-mahabharata-android"
TARGET_DIR = "/home/atharva/Downloads/VyasMahabharata"

def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    token_file = os.path.join(os.path.dirname(__file__), "../../.git_token")
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    return ""

TOKEN = get_token()

class NoAuthRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is not None and "blob.core.windows.net" in newurl:
            new_req.headers = {k: v for k, v in new_req.headers.items() if k.lower() != "authorization"}
        return new_req

def get_latest_run_id():
    url = f"https://api.github.com/repos/{REPO}/actions/runs?branch=main&per_page=1"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent"
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        runs = data.get("workflow_runs", [])
        if runs:
            return runs[0]["id"]
        return None

def get_run_status(run_id):
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent"
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def download_artifact(artifact_url):
    opener = urllib.request.build_opener(NoAuthRedirect())
    req = urllib.request.Request(artifact_url, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Antigravity-Agent"
    })
    
    os.makedirs(TARGET_DIR, exist_ok=True)
    zip_path = os.path.join(TARGET_DIR, "artifact.zip")
    
    print(f"Downloading APK artifact from: {artifact_url}")
    with opener.open(req) as resp, open(zip_path, "wb") as f:
        f.write(resp.read())
        
    print(f"Extracting artifact to {TARGET_DIR}...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(TARGET_DIR)
        extracted = z.namelist()
        
    if os.path.exists(zip_path):
        os.remove(zip_path)
    print(f"SUCCESS: Extracted APK files to {TARGET_DIR}: {extracted}")

def main():
    if not TOKEN:
        print("Error: No GitHub token provided in environment or .git_token")
        return 1

    target_run_id = None
    if len(sys.argv) > 1:
        target_run_id = sys.argv[1]
    else:
        print("Fetching latest workflow run on main...")
        for _ in range(10):
            target_run_id = get_latest_run_id()
            if target_run_id:
                break
            time.sleep(3)

    if not target_run_id:
        print("Error: Could not determine workflow run ID")
        return 1

    print(f"Monitoring GitHub Actions Run {target_run_id}...")
    max_attempts = 40  # 40 * 15s = 10 minutes
    for attempt in range(max_attempts):
        data = get_run_status(target_run_id)
        status = data.get("status")
        conclusion = data.get("conclusion")
        html_url = data.get("html_url")
        print(f"[{attempt+1}/{max_attempts}] Status: {status} | Conclusion: {conclusion} | {html_url}")
        
        if status == "completed":
            if conclusion == "success":
                print("Cloud compilation SUCCEEDED! Fetching artifacts...")
                art_url = f"https://api.github.com/repos/{REPO}/actions/runs/{target_run_id}/artifacts"
                req = urllib.request.Request(art_url, headers={
                    "Authorization": f"token {TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Antigravity-Agent"
                })
                with urllib.request.urlopen(req) as resp:
                    art_data = json.loads(resp.read().decode())
                    artifacts = art_data.get("artifacts", [])
                    if artifacts:
                        download_url = artifacts[0]["archive_download_url"]
                        download_artifact(download_url)
                        return 0
                    else:
                        print("Error: No artifacts found in run")
                        return 1
            else:
                print(f"Cloud build FAILED with conclusion: {conclusion}")
                return 1
        time.sleep(15)
        
    print("Timeout waiting for cloud build")
    return 1

if __name__ == "__main__":
    sys.exit(main())
