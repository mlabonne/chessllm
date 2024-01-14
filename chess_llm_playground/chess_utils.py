import io
import re
from datetime import datetime

import cairosvg
import chess
import gistyc
import numpy as np
import requests
from PIL import Image as PILImage


def generate_regex(board: chess.Board) -> str:
    """
    Generate a regex pattern that matches all legal moves for the given board.

    :param board: The chess board

    Based on a script made by 903124:
      https://gist.github.com/903124/cfbefa24da95e2316e0d5e8ef8ed360d # noqa E501
    See in Outlines:
      https://outlines-dev.github.io/outlines/cookbook/models_playing_chess/ # noqa E501

    """
    legal_moves = list(board.legal_moves)
    move_strings = [board.san(move) for move in legal_moves]
    move_strings = [re.sub(r"[+#]", "", move) for move in move_strings]
    regex_pattern = "|".join(re.escape(move) for move in move_strings)
    return regex_pattern


def write_pgn(
    pgn_moves, model_id_white, model_id_black, result, time_budget, termination
):
    # Get current UTC date and time
    current_utc_datetime = datetime.utcnow()
    utc_date = current_utc_datetime.strftime("%Y.%m.%d")
    utc_time = current_utc_datetime.strftime("%H:%M:%S")

    # Output the final PGN with CLKS and additional details
    final_pgn = f"""
            [Event 'Chess LLM Arena']
            [Site 'https://github.com/mlabonne/chessllm']
            [Date '{utc_date}']
            [White '{model_id_white}']
            [Black '{model_id_black}']
            [Result '{result}']
            [Time '{utc_time}']
            [TimeControl '{time_budget}+0']
            [Termination '{termination}']
            {pgn_moves}
            """

    return final_pgn


def determine_termination(board, time_budget_white, time_budget_black):
    """
    Determine the termination of the game.
    """
    if board.is_checkmate():
        return "Checkmate"
    elif board.is_stalemate():
        return "Stalemate"
    elif board.is_insufficient_material():
        return "Draw due to insufficient material"
    elif board.can_claim_threefold_repetition():
        return "Draw by threefold repetition"
    elif board.can_claim_fifty_moves():
        return "Draw by fifty-move rule"
    elif time_budget_white <= 0 or time_budget_black <= 0:
        return "Timeout"
    else:
        return "Unknown"


def create_gif(image_list, gif_path, duration):
    # Convert numpy arrays back to PIL images
    pil_images = [PILImage.fromarray(image) for image in image_list]

    # Save the images as a GIF
    pil_images[0].save(
        gif_path,
        save_all=True,
        append_images=pil_images[1:],
        duration=duration,
        loop=0,  # noqa E501
    )


def save_result_file(
    pgn_id, model_id_white, model_id_black, result, auth_token, gist_id
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Data to be written to the file
    data_str = f"{pgn_id},{timestamp},{model_id_white},{model_id_black},{result}\n"  # noqa E501

    # Append data to a text file
    with open("chessllm_results.csv", "a") as file:
        file.write(data_str)

    # Update the Gist
    gist_api = gistyc.GISTyc(auth_token=auth_token)

    gist_api.update_gist(file_name="chessllm_results.csv", gist_id=gist_id)


def save_pgn(final_pgn, file_name, auth_token):
    # Write final PGN to a file
    with open(file_name + ".pgn", "w") as file:
        file.write(final_pgn)

    gist_api = gistyc.GISTyc(auth_token=auth_token)
    response_data = gist_api.create_gist(file_name=file_name + ".pgn")

    return response_data["id"]


def download_file(base_url, file_name):
    # Unique query parameter to bypass cache (using a timestamp)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    url = f"{base_url}?ts={timestamp}"

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
    else:
        print(f"Failed to download file. HTTP status code: {response.status_code}")  # noqa E501


def init_board(time_budget):
    board = chess.Board()
    board_images = []
    pgn_moves = ""
    move_number = 1
    result = None
    time_budget_white, time_budget_black = time_budget, time_budget
    return (
        board,
        board_images,
        pgn_moves,
        move_number,
        time_budget_white,
        time_budget_black,
        result,
    )


def render_board_to_image(board, board_images):
    last_move = board.peek()  # Get the last move made
    svg = chess.svg.board(
        board=board, arrows=[(last_move.from_square, last_move.to_square)]
    ).encode("utf-8")
    png = cairosvg.svg2png(bytestring=svg)
    image = PILImage.open(io.BytesIO(png))
    board_images.append(np.array(image))
    return image
