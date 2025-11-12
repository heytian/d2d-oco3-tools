import requests
from pathlib import Path

# Path to your text file of URLs
links_file = "YOUR FILE PATH HERE"

# Folder to save the downloaded files
download_folder = Path("YOUR OUTPUT PATH HERE")
download_folder.mkdir(exist_ok=True)

# Your Earthdata bearer token
BEARER_TOKEN = "insert your token but remove it after processing and do not commit to git!"

# Read all links
with open(links_file, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

# Download files
for url in urls:
    filename = download_folder / url.split("/")[-1]
    print(f"Downloading {filename} ...")
    
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    r = requests.get(url, headers=headers, stream=True)
    
    if r.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Failed to download {url}: {r.status_code}")
