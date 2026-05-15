import os
import sys
import json
import urllib.request
import urllib.error

def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Cols
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for condition in win_conditions:
        a, b, c = condition
        if board[a] != ' ' and board[a] == board[b] == board[c]:
            return board[a]
    if ' ' not in board:
        return 'Draw'
    return None

def minimax(board, depth, is_maximizing):
    result = check_winner(board)
    if result == 'O':
        return 10 - depth
    elif result == 'X':
        return depth - 10
    elif result == 'Draw':
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                score = minimax(board, depth + 1, False)
                board[i] = ' '
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                score = minimax(board, depth + 1, True)
                board[i] = ' '
                best_score = min(score, best_score)
        return best_score

def get_best_move(board):
    best_score = -float('inf')
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'O'
            score = minimax(board, 0, False)
            board[i] = ' '
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

def post_comment_and_close(repo, issue_number, token, comment):
    if not repo or not issue_number or not token:
        print(f"Would comment on issue #{issue_number}: {comment}")
        return

    # Post comment
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Tic-Tac-Toe-Bot"
    }
    data = json.dumps({"body": comment}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(f"Error posting comment: {e}")

    # Close issue
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    data = json.dumps({"state": "closed"}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(f"Error closing issue: {e}")

def main():
    repo = os.environ.get("GITHUB_REPOSITORY")
    issue_number = os.environ.get("ISSUE_NUMBER")
    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_author = os.environ.get("ISSUE_AUTHOR", "Player")
    token = os.environ.get("GITHUB_TOKEN")

    if not issue_title.lower().startswith("move:"):
        print("Not a move issue.")
        sys.exit(0)

    try:
        move_str = issue_title.split(":")[1].strip()
        move = int(move_str) - 1
        if move < 0 or move > 8:
            raise ValueError()
    except (IndexError, ValueError):
        msg = f"@{issue_author} Invalid move format! The title must be exactly `move: <number>` where number is 1-9."
        post_comment_and_close(repo, issue_number, token, msg)
        sys.exit(1)

    state_file = "game/state.json"
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            state = json.load(f)
    else:
        state = {
            "board": [" "] * 9,
            "status": "active",
            "wins": 0, "losses": 0, "draws": 0,
            "message": "Your turn! (You play X)"
        }

    # Reset if game was over
    if state["status"] != "active":
        state["board"] = [" "] * 9
        state["status"] = "active"

    board = state["board"]

    if board[move] != ' ':
        msg = f"@{issue_author} Square {move + 1} is already occupied! Please choose another square."
        post_comment_and_close(repo, issue_number, token, msg)
        sys.exit(1)

    # Human Move
    board[move] = 'X'
    
    winner = check_winner(board)
    if winner:
        # Human won or draw
        if winner == 'X':
            state["status"] = "win"
            state["wins"] += 1
            state["message"] = f"Game over! @{issue_author} won! 🎉"
            msg = f"@{issue_author} won! Congrats!"
        else:
            state["status"] = "draw"
            state["draws"] += 1
            state["message"] = "Game over! It's a draw! 🤝"
            msg = f"It's a draw, @{issue_author}!"
    else:
        # Bot Move
        bot_move = get_best_move(board)
        if bot_move != -1:
            board[bot_move] = 'O'

        winner = check_winner(board)
        if winner == 'O':
            state["status"] = "loss"
            state["losses"] += 1
            state["message"] = f"Game over! The Bot won! 🤖"
            msg = f"The bot played square {bot_move + 1} and won! Better luck next time, @{issue_author}."
        elif winner == 'Draw':
            state["status"] = "draw"
            state["draws"] += 1
            state["message"] = "Game over! It's a draw! 🤝"
            msg = f"The bot played square {bot_move + 1}. It's a draw, @{issue_author}!"
        else:
            state["message"] = f"Bot played square {bot_move + 1}. Your turn, @{issue_author}!"
            msg = f"Bot played square {bot_move + 1}. It's your turn, @{issue_author}!"

    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

    # Render board and update README
    import render
    render.render_board(state)
    render.update_readme(state)

    post_comment_and_close(repo, issue_number, token, msg)

if __name__ == "__main__":
    main()
