import re

import pandas as pd
import requests
import zstandard as zstd
from tqdm import tqdm


def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True
    return False


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
                        white_elo = int(elo_pair[0]) if elo_pair[0] else white_elo  # noqa E501
                        black_elo = int(elo_pair[1]) if elo_pair[1] else black_elo  # noqa E501

                if white_elo and black_elo:
                    avg_elo = (white_elo + black_elo) / 2
                    games_data.append((avg_elo, game_content))

                current_game = []

            progress_bar.update(1)
        progress_bar.close()

    return pd.DataFrame(games_data, columns=["AverageElo", "Transcript"])


def decompress_file(compressed_file, decompressed_file):
    with open(compressed_file, "rb") as comp_file:
        dctx = zstd.ZstdDecompressor()
        with open(decompressed_file, "wb") as decomp_file:
            dctx.copy_stream(comp_file, decomp_file)


def sample_games(df, min_elo, max_elo, max_games):
    df = df[(df["AverageElo"] >= min_elo) & (df["AverageElo"] <= max_elo)]
    df = df.sort_values(by="AverageElo")

    increment = (max_elo - min_elo) / max_games
    sampled_games = []

    for i in tqdm(range(max_games), desc="Sampling Games"):
        target_elo = min_elo + i * increment
        closest_game = df.iloc[(df["AverageElo"] - target_elo).abs().argsort()[:1]]  # noqa E501
        sampled_games.append(closest_game)

    return pd.concat(sampled_games)


def save_games(games, filename):
    with open(filename, "w") as file:
        for game in games:
            file.write(game + "\n\n")
