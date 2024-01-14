from collections import defaultdict


def calculate_elo(rank1, rank2, result):
    """
    Calculate the new ELO rating for a player.
    :param rank1: The current ELO rating of player 1
    :param rank2: The current ELO rating of player 2
    :param result: 1 if player 1 wins, 0 if player 2 wins, 0.5 for a draw
    :return: The updated ELO rating of player 1
    """
    K = 32
    expected_score1 = 1 / (1 + 10 ** ((rank2 - rank1) / 400))
    new_rank1 = rank1 + K * (result - expected_score1)
    return round(new_rank1)


def update_elo_ratings(chess_data):
    """
    Update ELO ratings for each player based on the match results
         in the dataset.
    :param chess_data: DataFrame with chess match results
    :return: A dictionary with updated ELO ratings for each player
    """
    elo_ratings = defaultdict(lambda: 1000)  # Default ELO rating is 1000

    for index, row in chess_data.iterrows():
        if row["Result"] == "*":
            continue  # Skip ongoing games

        model1 = row["Model1"]
        model2 = row["Model2"]
        result = row["Result"]

        model1_elo = elo_ratings[model1]
        model2_elo = elo_ratings[model2]

        result = [float(x) for x in result.split("-")]
        # update ELO based on the result of the game
        elo_ratings[model1] = calculate_elo(model1_elo, model2_elo, result[0])
        elo_ratings[model2] = calculate_elo(model2_elo, model1_elo, result[1])

    return elo_ratings


def print_elo_ratings(
    model_id_white: str, model_id_black: str, elo_ratings_df, result: str
):
    """
    Print and update the ELO ratings of two models.

    :param model_id_white: The huggingface ID of the white model
    :param model_id_black: The huggingface ID of the black model
    :param elo_ratings_df: DataFrame with ELO ratings
    :param result: The result of the game

    """
    if result == "*":
        print("Ongoing game!")
        return

    elo_white = elo_ratings_df.loc[
        elo_ratings_df["Model"] == model_id_white, "ELO Rating"
    ].get(0, 1000)
    elo_black = elo_ratings_df.loc[
        elo_ratings_df["Model"] == model_id_black, "ELO Rating"
    ].get(0, 1000)

    result = [float(x) for x in result.split("-")]
    new_elo_white = calculate_elo(elo_white, elo_black, result[0])
    new_elo_black = calculate_elo(elo_black, elo_white, result[1])

    if result[0] > result[1]:
        print(f"{model_id_white} wins!")
    elif result[0] < result[1]:
        print(f"{model_id_black} wins!")
    else:
        print("Draw!")

    print_elo_change(
        model_id_white,
        model_id_black,
        elo_white,
        elo_black,
        new_elo_white,
        new_elo_black,
    )


def print_elo_change(
    model_id_white,
    model_id_black,
    elo_white,
    elo_black,
    new_elo_white,
    new_elo_black,
):
    print("ELO change:")

    print(
        (
            f"* {model_id_white}: {elo_white} -> {new_elo_white}"
            " ({new_elo_white - elo_white:+})"
        )
    )
    print(
        (
            f"* {model_id_black}: {elo_black} -> {new_elo_black}"
            " ({new_elo_black - elo_black:+})"
        )
    )
