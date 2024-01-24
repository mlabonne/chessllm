<div align="center">
  <h1>♟️ Chess LLM</h1>
  <p>
    ⚔️ <a href="https://huggingface.co/spaces/mlabonne/chessllm">Chess LLM Arena</a> •
    🏆 <a href="https://gist.github.com/chessllm/696115fe2df47fb2350fcff2663678c9">Leaderboard</a>
  </p>
  <p><em>Train your own chess LLM and compete in the arena!</em></p>
</div>

| Notebook          | Description                                                       | Notebook                                                                                                                                          |
| ----------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chess LLM Dataset | Create your own PGN dataset based on Lichess data and ELO scores. | <a href="https://colab.research.google.com/drive/11UjbfajCzphe707_V7PD-2e5WIzyintf?usp=sharing"><img src="img/colab.svg" alt="Open In Colab"></a> |
| Chess LLM Trainer | Train your own chess small language models on your datasets.      | <a href="https://colab.research.google.com/drive/1e2PszrvaY4Lv5SiRXuBGb5R4GdZsm-H3?usp=sharing"><img src="img/colab.svg" alt="Open In Colab"></a> |

# Installation

To install the utility package, run the following command in the root directory of the repository:

```bash
pip install -e . 
```

# Windows OS
- Install GTK3 Runtime 
- Add the bin path to chess_utils.py under os.add_dll_directory


# Install Stockfish
- Download Stockfish from https://stockfishchess.org/download/
- Place the stockfish-windows-x86-64-avx2 under stockfish folder in main project