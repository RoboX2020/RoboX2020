import json
import os

def render_board(state):
    board = state['board']
    
    # SVG Dimensions and settings
    width = 300
    height = 300
    cell_size = 100
    bg_color = "#1e1e1e"
    line_color = "#444444"
    x_color = "#ff5555"
    o_color = "#55ffff"
    
    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{width}" height="{height}" fill="{bg_color}"/>',
        # Grid lines
        f'<line x1="{cell_size}" y1="0" x2="{cell_size}" y2="{height}" stroke="{line_color}" stroke-width="4"/>',
        f'<line x1="{cell_size * 2}" y1="0" x2="{cell_size * 2}" y2="{height}" stroke="{line_color}" stroke-width="4"/>',
        f'<line x1="0" y1="{cell_size}" x2="{width}" y2="{cell_size}" stroke="{line_color}" stroke-width="4"/>',
        f'<line x1="0" y1="{cell_size * 2}" x2="{width}" y2="{cell_size * 2}" stroke="{line_color}" stroke-width="4"/>'
    ]
    
    # Draw Xs and Os
    for i in range(9):
        x = (i % 3) * cell_size
        y = (i // 3) * cell_size
        mark = board[i]
        
        if mark == 'X':
            svg.append(f'<line x1="{x + 20}" y1="{y + 20}" x2="{x + 80}" y2="{y + 80}" stroke="{x_color}" stroke-width="8" stroke-linecap="round"/>')
            svg.append(f'<line x1="{x + 80}" y1="{y + 20}" x2="{x + 20}" y2="{y + 80}" stroke="{x_color}" stroke-width="8" stroke-linecap="round"/>')
        elif mark == 'O':
            svg.append(f'<circle cx="{x + 50}" cy="{y + 50}" r="30" stroke="{o_color}" stroke-width="8" fill="none"/>')
            
    svg.append('</svg>')
    
    with open("board.svg", "w") as f:
        f.write("\n".join(svg))

def update_readme(state):
    with open("README.md", "r") as f:
        content = f.read()
        
    start_tag = "<!-- GAME_START -->"
    end_tag = "<!-- GAME_END -->"
    
    if start_tag not in content or end_tag not in content:
        print("Could not find GAME_START and GAME_END tags in README.md")
        return
        
    before = content.split(start_tag)[0]
    after = content.split(end_tag)[1]
    
    # Generate the markdown
    status_msg = state.get('message', 'Your turn! (You play X)')
    
    new_content = [
        start_tag,
        "### 🎮 Play Tic-Tac-Toe with me!",
        f"**{status_msg}**",
        "",
        "| Stats | Score |",
        "| --- | --- |",
        f"| 🏆 Wins | {state['wins']} |",
        f"| 💀 Losses | {state['losses']} |",
        f"| 🤝 Draws | {state['draws']} |",
        "",
        "![Tic-Tac-Toe Board](board.svg)",
        "",
        "#### Make your move:"
    ]
    
    if state['status'] != 'active':
        new_content.extend([
            "Game over! Click any cell to start a new game.",
            ""
        ])
    
    # Numpad grid for moves
    repo = "RoboX2020/RoboX2020"
    base_url = f"https://github.com/{repo}/issues/new?template=move.md&title=move:+"
    
    new_content.extend([
        "<table>",
        "  <tr>"
    ])
    for i in range(1, 10):
        # Disable links for occupied cells if the game is active
        if state['status'] == 'active' and state['board'][i-1] != ' ':
            new_content.append(f'    <td align="center" width="50" height="50">⬜</td>')
        else:
            new_content.append(f'    <td align="center" width="50" height="50"><a href="{base_url}{i}"><b>{i}</b></a></td>')
        if i % 3 == 0:
            new_content.append("  </tr>")
            if i != 9:
                new_content.append("  <tr>")
    new_content.extend([
        "</table>",
        "",
        "---",
        "*How it works: When you click a number, it opens an issue. A GitHub Action runs a Python script that calculates the bot's move using Minimax, updates the SVG board, and commits the result back!*",
        end_tag
    ])
    
    with open("README.md", "w") as f:
        f.write(before + "\n".join(new_content) + after)

if __name__ == "__main__":
    if os.path.exists("game/state.json"):
        with open("game/state.json", "r") as f:
            state = json.load(f)
    else:
        print("game/state.json not found")
        state = {
            "board": [" "] * 9,
            "status": "active",
            "wins": 0, "losses": 0, "draws": 0,
            "message": "Your turn! (You play X)"
        }
    render_board(state)
    update_readme(state)
