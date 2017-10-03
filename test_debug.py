from random import randint
import numpy as np

game_over = False # game state
# will alternate during gameplay
cur_player = 1 
other_player = 2

# size N x N
board_size = 6
row_indices = []
col_indices = []

# create board indexing
for i in range(board_size):
    row_indices.append(str(i))
    col_indices.append(chr(ord('A') + i))

# 2 sets of empty boards
board_attacks = np.array([[[]],[[]]]*2) # 2 empty attack marker boards (GUI)
board_ships = np.array([[[]],[[]]]*2) # 2 empty ship location boards (hidden)

tile_types = ['S', 'M', 'L', 'X'] # types of ship tiles
tile_reveal_types = ['M', 'H', ' '] # hit, miss, or sunken

# types of ships
ship_archive = {"small": 2, \
                "medium": 3, \
                "large": 4, \
                "xlarge": 5, \
               }

total_ship_tiles = sum([v for k,v in ship_archive.items()]) # tiles per player
# how many left per player and per ship
remaining = {"total": np.array([total_ship_tiles]*2)}
for i in range(len(ship_archive)):
    remaining[tile_types[i]] = np.array([i+2]*2)


'''
@global game_over:  - A "fail-safe" to prevent
                      infinite looping.
                    - If end_game() fails for any reason,
                      game will terminate.

The main algorithm/loop of the game.

This is where player 1 and player 2 attack
each other via alternating input until
someone wins or 'quit' is typed in.
'''
def game_main():
    global game_over
    global cur_player
    global other_player
    
    while not game_over:
        guess = raw_input("Player " + str(cur_player) + " guess: ")
        guess = guess.strip()
        
        if not guess == 'quit':
            if len(guess) != 2:
                print "Error: Please enter a valid target (E.g. \'B7\')\n"
                continue
            elif guess[0] not in col_indices or\
                 guess[1] not in row_indices:
                print "Error: Oops, please enter a target within the board (E.g. \'B7\')\n"
                continue
            else:
                row = int(guess[1])
                col = ord(guess[0]) - ord('A')
                
                tile = board_ships[other_player-1,row, col]
                attacked = False
                if board_attacks[other_player-1, row, col] in tile_reveal_types:
                    attacked = True
        
                if not attacked:
                    print "Valid attack type, checking tile..."
                    if tile in tile_types:
                        board_attacks[other_player-1,row, col] = 'H'
                        remaining[tile][other_player-1] -= 1
                        remaining['total'][other_player-1] -= 1
                            
                        if remaining[tile][other_player-1] == 0:
                            
                            sink_ship(other_player, tile)
                            if remaining["total"][other_player-1] == 0:
                                game_over = True
                                print "It's a hit, you sunk ALL of player " + str(other_player) + "\'s ships!"
                                end_game(cur_player)
                            else:
                                print "It's a hit, you sunk one of player " + str(other_player) + "\'s ships!"
                        else:
                            print "It's a hit!"
                        print "hits until loss: "+ str(remaining["total"][other_player-1]) +\
                              "\'"+ tile +", \' tiles left: "+str(remaining[tile][other_player-1])
                    else:
                        print "It's a miss"
                        if tile == '.':
                            board_attacks[other_player-1,row, col] = 'M'
                else:
                    print "That place was already attacked (fooled you twice, shame on you)..."
                
            print_boards(board_attacks)
            cur_player, other_player = other_player, cur_player
        else:
            end_game(0)
            break


'''
Display the welcome screen with rules.
Prompt user to start the game.
Initialize the board and display fresh GUI
'''
def start_game():
    global board_size
    print "~Welcome to BATTLESHIP~"
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    print ""
    print "How To Play: "
    print "1. There is a " + str(board_size) + "x" + str(board_size) + " board, this is the ocean with ships:"
    print "      ACROSS: letters A-" + chr(ord('A')+board_size-1)
    print "      DOWN: numbers 0-" + str(board_size-1)
    print "" 
    print "2. Take a guess shot by typing in a location like this:"
    print "      Examples: A2, B3, F7, E4, ..., and so on"
    print ""
    print "3. Each player takes turns (2-player)"
    print "4. Win by sinking the other player's ships!"
    print ""
    print "(P.S. Type in \'quit' to QUIT)"
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    print ""
    raw_input("Press \'ENTER\' to START: ")
    print ""
    print ""
    print ""
    init_board()
    print "GAME READY!\n"
    print_boards(board_attacks)
    game_main()


'''
Try to set up the game until
we find a configuration that works.
'''
def init_board():
    print "Configuring board layout..."
    if board_size < max([v for k,v in ship_archive.items()]):
        print "\nBoard too small for ships"
        print "Exiting game..."
        quit()
    while not init_board_helper():
        continue


'''
Actually set up the game (attempt).
Will cancel and restart if timer reaches 0.
'''
def init_board_helper():
    global board_attacks
    global board_ships
    board_attacks = np.array([[['.']*board_size]*board_size]*2, dtype = object)
    board_ships = np.array([[['.']*board_size]*board_size]*2, dtype = object)
    
    for player in range (1,3):
        for ship in ship_archive:
            placed = False
            size = ship_archive[ship]
            timeout = 1000
            while not placed:
                row, col, drc = randint(0,board_size-1), randint(0,board_size-1), randint(0,3)
                if can_place(player, size, row, col, drc):
                    place_ship(player, size, row, col, drc)
                    placed = True
                else:
                    timeout -= 1
                    if timeout == 0:
                        print_boards(board_ships)
                        reset_board()
                        return False
    return True


'''
Unable to place ship, bad setup.
For when init_board_helper() needs to
retry the random board layout.
'''
def reset_board():
    global board_ships
    board_ships.fill('.')
    print "TIMEOUT, setup fail, resetting..."

'''
@param board: both player 1 and 2's boards

Display GUI with all hits/misses on each player.
Player 1 on the left, Player 2 on the right.
'''
def print_boards(boards):
    print ('  ' + " ".join(col_indices) + '  ')*2
    print ('  ' + " ".join('-'*board_size) + '  ')*2
    
    for i in range(board_size):
        print str(i) + '|' + " ".join(boards[0,i]) + "  " +\
              str(i) + '|' + " ".join(boards[1,i]) + "  "
    print ""


'''
@param player: 1 or 2
@param size: length of ship
@param row, col:location of first tile
@param drc: 0 = up
            1 = right
            2 = down
            3 = left
            
Check if ship can be placed in a certain way.
'''
def can_place(player, size, row, col, drc):
    global board_ships
    direc = ""
    try:
        print""
        for i in range(size):
            print "tile: "+str(i)
            if drc == 0:
                direc = 'up'
                if board_ships[player-1, row-i, col] in tile_types or row-i < 0:
                    print "FAIL: size: " + str(size) + ", row,col: " +\
                           str(row) + ',' + str(col) + " , drc: " + direc
                    return False
            elif drc == 1:
                direc = 'right'
                if board_ships[player-1, row, col+i] in tile_types or col+i > 9:
                    print "FAIL: size: " + str(size) + ", row,col: " +\
                           str(row) + ',' + str(col) + " , drc: " + direc
                    return False
            elif drc == 2:
                direc = 'down'
                if board_ships[player-1, row+i, col] in tile_types or row+i > 9:
                    print "FAIL: size: " + str(size) + ", row,col: " +\
                           str(row) + ',' + str(col) + " , drc: " + direc
                    return False
            elif drc == 3:
                direc = 'left'
                if board_ships[player-1, row, col-i] in tile_types or col-i < 0:
                    print "FAIL: size: " + str(size) + ", row,col: " +\
                           str(row) + ',' + str(col) + " , drc: " + direc
                    return False
    except:
        print "EXCEPTION OUT OF BOUNDS: size: " + str(size) + ", row,col: " +\
               str(row) + ',' + str(col) + " , drc: " + direc
        return False
    return True


'''
@param player: 1 or 2
@param size: length of ship
@param row, col:location of first tile
@param drc: 0 = up
            1 = right
            2 = down
            3 = left
            
Place ship on the board.
'''
def place_ship(player, size, row, col, drc):
    global board_ships
    tile = tile_types[size-2]
    direc = ""
    for i in range(size):
        if drc == 0:
            direc = 'up'
            board_ships[player-1, row-i, col] = tile
        elif drc == 1:
            direc = 'right'
            board_ships[player-1, row, col+i] = tile
        elif drc == 2:
            direc = 'down'
            board_ships[player-1, row+i, col] = tile
        elif drc == 3:
            direc = 'left'
            board_ships[player-1, row, col-i] = tile
            
    print "SUCCESS: size: " + str(size) + ", row,col = " + str(row) + ',' + str(col) +\
          " , drc: " + direc + " " + ", type: \'"+ tile + "\'"
    print_boards(board_ships)


'''
@param other_player: he player being attacked
@param tile_type: char representing ship type

Hit was successful and no more remaining tiles
of that type of ship for the attacked player
'''
def sink_ship(other_player, tile_type):
    global board_ships
    global board_attacks
    global board_size
    
    for i in range(board_size):
        for j in range(board_size):
            if board_ships[other_player-1, i, j] == tile_type:
                board_attacks[other_player-1, i, j] = " "
        
'''
@param player:  0 = force quit
                1 = player 1 wins
                2 = player 2 wins
                
Exit the game
'''
def end_game(player):
    global board_attacks
    if player > 0:
        print "Player", player, "Wins!"
        print_boards(board_attacks)
    print "G A M E___O V E R"  
    quit()
    
start_game()   # Start the game
 
