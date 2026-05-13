# Matoi Demo -- generates demo.gif for README
# Run: vhs demo.tape

Output demo.gif
Set Width 1200
Set Height 800
Set FontSize 16
Set FontFamily "JetBrains Mono"
Set Theme "Catppuccin Mocha"
Set Padding 20

# Start matoi
Type "matoi"
Enter
Sleep 3s

# Select PM -- Oliver (Startup)
Down 3
Sleep 500ms
Enter
Sleep 2s

# Enter goal
Type "build a browser tetris game"
Enter
Sleep 1s

# Auto team
Enter
Sleep 3s

# Session started -- type task
Sleep 2s
Type "create the game with all 7 tetrominoes, scoring, levels, and pause"
Enter

# Wait for agents to respond
Sleep 15s

# Show cost
Type "/cost"
Enter
Sleep 3s

# Exit
Type "exit"
Enter
Sleep 3s
