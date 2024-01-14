import numpy as np
import pandas as pd
from tqdm import tqdm


def sample_games(df, min_elo, max_elo, max_games):
    """
    Create a dataset of `max_games` games between `min_elo` and `max_elo`.

    This function is used to create the curriculum dataset.

    :param df: DataFrame with chess match results
    :param min_elo: Minimum ELO rating
    :param max_elo: Maximum ELO rating
    :param max_games: Maximum number of games to sample
    :return: A DataFrame with sampled games

    """
    df = df[(df["AverageElo"] >= min_elo) & (df["AverageElo"] <= max_elo)]
    df = df.sort_values(by="AverageElo")

    increment = (max_elo - min_elo) / max_games
    sampled_games = []

    for i in tqdm(range(max_games), desc="Sampling Games"):
        target_elo = min_elo + i * increment
        closest_game = df.iloc[(df["AverageElo"] - target_elo).abs().argsort()[:1]]  # noqa E501
        sampled_games.append(closest_game)

    return pd.concat(sampled_games)


def random_sampling(df, min_elo, max_elo, max_games):
    """Create a dataset of `max_games` random games between `min_elo` and `max_elo`."""

    filtered_games = df[(df["average_elo"] >= min_elo) & (df["average_elo"] <= max_elo)]

    # Randomly sample up to max_games
    if len(filtered_games) > max_games:
        sampled_games = filtered_games.sample(
            n=max_games, random_state=np.random.RandomState()
        )
    else:
        sampled_games = filtered_games

    return sampled_games


def curriculum_sampling(df, min_elo, max_elo, max_games):
    """Create an ordered dataset of `max_games` random games between `min_elo` and `max_elo`."""

    # Use random_sampling to get a random subset of games
    sampled_games = random_sampling(df, min_elo, max_elo, max_games)

    # Order the sampled games by average_elo
    ordered_games = sampled_games.sort_values(by="average_elo")

    return ordered_games
