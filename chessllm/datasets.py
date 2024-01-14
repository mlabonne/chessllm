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
    total_lines = sum(1 for _ in open(file_path, "r"))
    games_data = []
    current_game = []
    elo_regex = re.compile(r"\[WhiteElo \"(\d+)\"\]|\[BlackElo \"(\d+)\"\]")

    with open(file_path, "r") as file:
        progress_bar = tqdm(total=total_lines, desc="Parsing Games")
        for line in file:
            stripped_line = line.strip()
            current_game.append(stripped_line)
            if stripped_line == "":
                game_content = "\n".join(current_game)
                elos = elo_regex.findall(game_content)

                white_elo, black_elo = 0, 0
                if elos:
                    for elo_pair in elos:
                        white_elo = int(elo_pair[0]) if elo_pair[0] else white_elo
                        black_elo = int(elo_pair[1]) if elo_pair[1] else black_elo

                if white_elo and black_elo:
                    avg_elo = (white_elo + black_elo) / 2
                    games_data.append((avg_elo, game_content))

                current_game = []

            progress_bar.update(1)
        progress_bar.close()

    return pd.DataFrame(games_data, columns=["average_elo", "transcript"])


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
