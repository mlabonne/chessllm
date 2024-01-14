import os
import re

import pandas as pd
import requests
import zstandard as zstd
from huggingface_hub import HfApi, create_repo
from tqdm import tqdm


def download_file(url):
    """
    Download a file from a URL and save it to the current directory.
    """
    # Extract filename from the URL
    filename = url.split("/")[-1]

    # Check if the file already exists
    if not os.path.exists(filename):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return filename, True

    return filename, False


def parse_and_store_games(file_path):
    filtered_lines = []

    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('[WhiteElo') or line.startswith('[BlackElo') or line.strip().startswith('1.'):
                filtered_lines.append(line.strip())

    games_data = []
    for i in range(0, len(filtered_lines) - 2, 3):
        try:
            white_elo = int(filtered_lines[i].split('"')[1])
            black_elo = int(filtered_lines[i + 1].split('"')[1])
            average_elo = (white_elo + black_elo) / 2
        except (ValueError, IndexError):
            # Skip the game if there's an issue with Elo ratings or index
            continue

        transcript = filtered_lines[i + 2]
        games_data.append({'average_elo': average_elo, 'transcript': transcript})

    return pd.DataFrame(games_data)


def decompress_file(compressed_file):
    # Derive the decompressed filename
    decompressed_file = compressed_file.rsplit(".", 1)[0] + ".pgn"

    # Check if the decompressed file already exists
    if not os.path.exists(decompressed_file):
        with open(compressed_file, "rb") as comp_file:
            dctx = zstd.ZstdDecompressor()
            with open(decompressed_file, "wb") as decomp_file:
                dctx.copy_stream(comp_file, decomp_file)
        return decompressed_file, True
    return decompressed_file, False


def upload_to_hf(username, repo_name):
    api = HfApi()
    # Create empty repo
    create_repo(
        repo_id=f"{username}/{repo_name}",
        repo_type="dataset",
        exist_ok=True,
    )
    # Upload gguf files
    api.upload_folder(
        repo_id=f"{username}/{repo_name}",
        repo_type="dataset",
        folder_path="dataset",
    )


def save_games(games, filename):
    with open(filename, "w") as file:
        for game in games:
            file.write(game + "\n\n")


def format_games(max_games):
    """
    Format the number of games to a human-readable string.
    """
    if max_games < 1000:
        return str(max_games)
    elif max_games < 1_000_000:
        return f"{max_games // 1000}k"
    elif max_games < 1_000_000_000:
        return f"{max_games // 1_000_000}M"
    else:
        return f"{max_games // 1_000_000_000}B"
