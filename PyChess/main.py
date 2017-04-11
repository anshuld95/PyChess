# Spring 2016 COMS 3101 Python Project
# Author - Anshul Doshi UNI - ad3222
# Chess.py - simulate 2 player chess

"""
This program uses a board data structure containing three things. 
	
	piece color - to differentiate between black and white

	piece type - froma collection of pawn, rook, knight, bishop etc..

	piece image - to actually display the piece in the window

With this data structure, we simulate chess between 2 players.

USAGE:
pythonw main.py (runs much better with pythonw)
"""
import pygame, random, sys
from pygame.locals import *

BOARDWIDTH = 8  
BOARDHEIGHT = 8
CAPTUREDROW = 4 # for our captured pieces box on side
SPACESIZE = 64 # size of each square
NUMPIECES = 6 # number of different pieces in a set

FPS = 30 
WINDOWWIDTH = 800
WINDOWHEIGHT = 600

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE)/2) - 100
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE)/2)

#			R    G  B
LIGHTTAN = (238,238,210)
TAN = (154, 91, 26)
GREEN = (118, 150, 86)
WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE  = (0,0,255)
PURPLE    = (255,   0, 255)

HIGHLIGHTCOLOR = WHITE
BGCOLOR = GREEN
TEXTCOLOR = BLACK
GRIDCOLOR = BLUE

EMPTY_SPACE = -1
EMPTY = None
PLAYER1 = 'player1'
PLAYER2 = 'player2'
PIECES = ['R', 'N', 'B', 'Q', 'K', 'P']

def main():
	global FPSCLOCK, DISPLAYSURF, WHITEPIECES, BLACKPIECES, BOARDRECTS, BASICFONT, CAPTURED, captureBoard

	#standard way to start a game
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('Chess')
	BASICFONT = pygame.font.Font('freesansbold.ttf', 36)

	#load images/pieces
	WHITEPIECES = {}
	BLACKPIECES = {}
	for c in PIECES:
		wpieceImg = pygame.image.load('images/White %s.png' % c, 'png')
		bpieceImg = pygame.image.load('images/Black %s.png' % c, 'png')
		if wpieceImg.get_size() != (SPACESIZE, SPACESIZE):
			wpieceImg = pygame.transform.smoothscale(wpieceImg, (SPACESIZE,SPACESIZE))
		WHITEPIECES[c] = wpieceImg
		if bpieceImg.get_size() != (SPACESIZE, SPACESIZE):
			bpieceImg = pygame.transform.smoothscale(bpieceImg, (SPACESIZE,SPACESIZE))
		BLACKPIECES[c] = bpieceImg

	#create underlying board structure to draw
	BOARDRECTS = []
	for x in range(BOARDWIDTH):
		BOARDRECTS.append([])
		for y in range(BOARDHEIGHT):
			r = pygame.Rect((XMARGIN + (x * SPACESIZE),
							 YMARGIN + (y * SPACESIZE),
							 SPACESIZE,
							 SPACESIZE))
			BOARDRECTS[x].append(r)
	# create captured board structure 
	CAPTURED = []
	for x in range(CAPTUREDROW):
		CAPTURED.append([])
		for y in range(BOARDHEIGHT):
			r = pygame.Rect((XMARGIN+550 + (x * SPACESIZE//2),
							 YMARGIN+130 + (y * SPACESIZE//2),
							 SPACESIZE//2,
							 SPACESIZE//2))
			CAPTURED[x].append(r)

	captureBoard = [[0 for i in range(CAPTUREDROW)] for j in range(BOARDHEIGHT)]

	# run forever
	while True:
		runGame()

def runGame():
	gameBoard = getBlankBoard()
	DISPLAYSURF.fill(BGCOLOR)
	drawBoard(gameBoard)

	selectedPieceType = None
	lastMouseDownX = None
	lastMouseDownY = None
	checkmate = False
	check = False
	checkingPiece = (0,0)
	turn = PLAYER1

	while True: # main game loop
		clickedSpace = None
		selectedPieceLoc = None

		# Gets Top text to show whose turn it is
		if turn == PLAYER1:
			p1 = BASICFONT.render("Player 1's Turn", True, BLACK, GREEN)
			p1Rect = p1.get_rect()
			p1Rect.center = (300,20)
			DISPLAYSURF.blit(p1, p1Rect)
		else:
			p2 = BASICFONT.render("Player 2's Turn", True, BLACK, GREEN)
			p2Rect = p2.get_rect()
			p2Rect.center = (300,20)
			DISPLAYSURF.blit(p2, p2Rect)

		for event in pygame.event.get(): # event handling loop
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == KEYUP and event.key == K_BACKSPACE:
				return # start a new game

			elif event.type == MOUSEBUTTONUP:
				if checkmate:
					return # after games ends, click to start a new game

				if event.pos == (lastMouseDownX, lastMouseDownY):
					# This event is a mouse click, not the end of a mouse drag.
					clickedSpace = locatePieceClick(event.pos)
				else:
					# this is the end of a mouse drag 
					# we have a selected piece with starting and target destination
					selectedPieceType = checkForPieceClick(gameBoard,(lastMouseDownX, lastMouseDownY))
					selectedPieceLoc = locatePieceClick((lastMouseDownX,lastMouseDownY))
					clickedSpace = locatePieceClick(event.pos)
					myPos = (selectedPieceLoc['x'], selectedPieceLoc['y'])
					myType = getPieceType(gameBoard, myPos)
					# for x, y in getMovableSet(gameBoard, selectedPieceType, selectedPieceLoc):
					# 		print("Highlighting: ", x, y)
					# 		highlightSpace(x, y)

					# check if a move is valid
					if isValid(gameBoard, selectedPieceType, selectedPieceLoc, clickedSpace, turn, check, checkingPiece):
						#print("VALID Move")
						# check = Check(gameBoard, myType, selectedPieceType, clickedSpace)
						# if check:
						# 	print("CHECK!")
						# 	checkingPiece = (selectedPieceType, clickedSpace)

						# update board and then reverse it for next player
						gameBoard = movePieceBoard(gameBoard, selectedPieceLoc, clickedSpace)
						drawBoard(gameBoard)
						reverseBoard(gameBoard)
						if turn == PLAYER1:
							turn = PLAYER2
						else:
							turn = PLAYER1
						drawBoard(gameBoard)
					else:
						# if not part of a valid drag, deselect both
						selectedPieceType = None
						selectedPieceLoc = None
						clickedSpace = None
			elif event.type == MOUSEBUTTONDOWN:
				# this is the start of a mouse click or mouse drag
				lastMouseDownX, lastMouseDownY = event.pos
		#reverseBoard(gameBoard)
		#drawBoard(gameBoard)
		pygame.display.update()
		FPSCLOCK.tick(FPS)

# This funtion initilializes our underlying data structure. A 8x8 array holding
# three values, color of piece, type of piece and the image of the piece
def getBlankBoard():
	board = [[0 for i in range(BOARDWIDTH)] for j in range(BOARDHEIGHT)]
	#print(board)
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if y == 0:
				if x == 0 or x == 7:
					board[x][y] = ('black', 'R', BLACKPIECES['R'])
				if x == 1 or x == 6:
					board[x][y] = ('black', 'N',BLACKPIECES['N'])
				if x == 2 or x == 5:
					board[x][y] = ('black', 'B', BLACKPIECES['B'])
				if x == 3:
					board[x][y] = ('black', 'Q',BLACKPIECES['Q'])
				if x == 4:
					board[x][y] = ('black', 'K', BLACKPIECES['K'])
			elif y == 1:
				board[x][y] = ('black', 'P', BLACKPIECES['P'])
			elif y == 6:
				board[x][y] = ('white', 'P', WHITEPIECES['P'])
			elif y == 7:
				if x == 0 or x == 7:
					board[x][y] = ('white', 'R', WHITEPIECES['R'])
				if x == 1 or x == 6:
					board[x][y] = ('white', 'N', WHITEPIECES['N'])
				if x == 2 or x == 5:
					board[x][y] = ('white', 'B', WHITEPIECES['B'])
				if x == 3:
					board[x][y] = ('white', 'Q', WHITEPIECES['Q'])
				if x == 4:
					board[x][y] = ('white', 'K', WHITEPIECES['K'])
			else:
				board[x][y] = EMPTY
	#print(board)
	return board

#Here we draw the board. First put all the rectangles with alternating colors. Then
# add the pieces in thier starting positions
def drawBoard(board):
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			#pygame.draw.rect(DISPLAYSURF, BLUE, BOARDRECTS[x][y], 1)
			if not (x % 2) and (y % 2):
				pygame.draw.rect(DISPLAYSURF, TAN, BOARDRECTS[x][y], 0)		
			elif (x % 2) and not (y % 2):
				pygame.draw.rect(DISPLAYSURF, TAN, BOARDRECTS[x][y], 0)
			else:
				pygame.draw.rect(DISPLAYSURF, LIGHTTAN, BOARDRECTS[x][y], 0)
			if board[x][y]:
				DISPLAYSURF.blit(board[x][y][2], BOARDRECTS[x][y])
	for i in range(CAPTUREDROW):
		for j in range(BOARDHEIGHT):
			pygame.draw.rect(DISPLAYSURF, BLACK, CAPTURED[i][j], 1)

# After a player makes a move we reverse the board by swapping all the indices
# in this special way
def reverseBoard(board):
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT//2):
			pieceInfo = board[x][y]
			board[x][y] = board[BOARDWIDTH-x-1][BOARDHEIGHT-y-1]
			board[BOARDWIDTH-x-1][BOARDHEIGHT-y-1] = pieceInfo 


# this function checks if a click was indeed on the board and whether a piece was there
def checkForPieceClick(board, pos):
	# See if the mouse click was on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
        	if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]) and board[x][y] != EMPTY:
        		return board[x][y][1]
    return None # Click was not on the board.

#this function returns the kind of piece there is at a certain location
def getPieceType(board, pos):
	if pos[0] < BOARDWIDTH and pos[1] < BOARDHEIGHT:
		if board[pos[0]][pos[1]] != EMPTY:
			return board[pos[0]][pos[1]][0]
		else:
			return None
#this function gives a dictionary of piece's location
def locatePieceClick(pos):
	# See if the mouse click was on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if BOARDRECTS[x][y].collidepoint(pos[0], pos[1]):
                return {'x': x, 'y': y}
    return None # Click was not on the board.

# this function was meant to highlight spaces but is never used
def highlightSpace(x, y):
	pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, BOARDRECTS[x][y], 0)

# This function tests whther a move is valid by checking whether the target location
# is indeed in a specific piece's set of possible moves. The check code here is never run 
# since its implementation causes issues
def isValid(board, piece, source_loc, target_loc, turn, check, checkingPiece):
	if piece == None or source_loc == None or target_loc == None:
		return False
	if turn  == PLAYER1:
		myType = 'white'
	else:
		myType = 'black'
	sourcePiece = board[source_loc['x']][source_loc['y']]
	if sourcePiece[0] != myType:
		return False
	# The check function hasn't been implemented correctly so its function call is commented out
	if check:
		oldBoard = board.copy()
		newBoard = movePieceBoard(oldBoard, source_loc, target_loc)
		#list_moves = getMovableSet(newBoard, checkingPiece[0], checkingPiece[1])
		for x in range(BOARDWIDTH):
			for y in range(BOARDHEIGHT):
				if newBoard[x][y] != EMPTY:
					if newBoard[x][y][0] == myType and newBoard[x][y][1] == 'K':
						kingLoc = (x, y)
						print("kingLoc = ", kingLoc)
		print("CheckingPiece", checkingPiece)
		oldPiece = newBoard[BOARDWIDTH-checkingPiece[1]['x']-1][BOARDHEIGHT-checkingPiece[1]['y']-1]
		print("oldpiece: ",oldPiece)
		x = checkingPiece[1]['x'] 
		y = checkingPiece[1]['y'] 
		newLoc = {'x': BOARDWIDTH-x-1, 'y': BOARDHEIGHT-y-1}
		if oldPiece != EMPTY and oldPiece != myType:
			listMoves = getMovableSet(newBoard, checkingPiece[0], newLoc)
			print("listMoves: ",listMoves)
			if kingLoc in listMoves:
				return False
	# check the movable list to see if target location is in it
	MovableSet = getMovableSet(board, piece, source_loc)
	#print(MovableSet)
	if (target_loc['x'], target_loc['y']) in MovableSet:
		return True
	else:
		return False

# this is an attempt to detect for checks. Its call is commented out due to issues that 
# arise from this implementation
def Check(board, myType, pieceName, target_loc):
	if myType == 'white':
		other = 'black'
	else:
		other = 'white'
	checkingPiece = (pieceName, target_loc)
	fullList = getMovableSet(board, pieceName, target_loc)
	#kingLoc = None
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			if board[x][y] != EMPTY:
				if board[x][y][0] == other and board[x][y][1] == 'K':
					kingLoc = (x, y) 
	#print("kingLoc = ", kingLoc)
	#print(fullList)
	if kingLoc in fullList:
		return True
	else:
		return False

# This function conducts the move, updating the board data structure
def movePieceBoard(board, source_loc, target_loc):
	pieceToMove = board[source_loc['x']][source_loc['y']]
	board[source_loc['x']][source_loc['y']] = None
	if board[target_loc['x']][target_loc['y']] == EMPTY:
		board[target_loc['x']][target_loc['y']] = pieceToMove
	else:
		capturePiece = board[target_loc['x']][target_loc['y']]
		putCapture(capturePiece)
		board[target_loc['x']][target_loc['y']] = None
		board[target_loc['x']][target_loc['y']] = pieceToMove
	return board

# when a piece is captruesd, this function puts its image in the captured pieces data 
# structure
def putCapture(piece):
	piece = list(piece)
	piece[2] = pygame.transform.smoothscale(piece[2], (SPACESIZE//2,SPACESIZE//2))
	if piece[0] == 'black' and piece[1] == 'P':
		x = 0
		y = 0
		while captureBoard[x][y] != 0 and y < BOARDHEIGHT:
			y = y+1
		captureBoard[x][y] = piece[2]
		DISPLAYSURF.blit(captureBoard[x][y], CAPTURED[x][y])	
	elif piece[0] == 'black' and piece[1] != 'P':
		x = 1
		y = 0
		while captureBoard[x][y] != 0 and y < BOARDHEIGHT:
			y = y+1
		captureBoard[x][y] = piece[2]
		DISPLAYSURF.blit(captureBoard[x][y], CAPTURED[x][y])
	elif piece[0] == 'white' and piece[1] == 'P':
		x = 2
		y = 0
		while captureBoard[x][y] != 0 and y < BOARDHEIGHT:
			y = y+1
		captureBoard[x][y] = piece[2]
		DISPLAYSURF.blit(captureBoard[x][y], CAPTURED[x][y])
	elif piece[0] == 'white' and piece[1] != 'P':
		x = 3
		y = 0
		while captureBoard[x][y] != 0 and y < BOARDHEIGHT:
			y = y+1
		captureBoard[x][y] = piece[2]
		DISPLAYSURF.blit(captureBoard[x][y], CAPTURED[x][y])
	#print("captured[x][y]", captureBoard)

# This is the main part of the code that calculates each pieces possible moveset,
# detecting for other pieces and enemy captures in the process. 
def getMovableSet(board, piece, source_loc):
	MovableSet = []
	x = source_loc['x']
	y = source_loc['y']
	sourcePieceType = getPieceType(board, (x,y))
	if piece == 'P':
		if y == 6:
			if board[x][y-1] == EMPTY and board[x][y-2] == EMPTY:
				MovableSet.append((x,y-1))
				MovableSet.append((x,y-2))
		if getPieceType(board, (x+1, y-1)) != None and getPieceType(board,(x+1, y-1)) != sourcePieceType:
			MovableSet.append((x+1,y-1))
		if getPieceType(board, (x-1, y-1)) != None and getPieceType(board,(x-1, y-1)) != sourcePieceType:
			MovableSet.append((x-1,y-1))
		if board[x][y-1] == EMPTY:
			MovableSet.append((x, y-1))
	if piece == 'R':
		i = 1
		while x-i >= 0: 
			if board[x-i][y] == EMPTY:
				MovableSet.append((x-i, y))
			elif getPieceType(board, (x-i, y)) != sourcePieceType:
				MovableSet.append((x-i, y))
				break
			else:
				break
			i = i+1
		i = 1
		while x+i < BOARDWIDTH:
			if board[x+i][y] == EMPTY:
				MovableSet.append((x+i, y))
			elif getPieceType(board, (x+i, y)) != sourcePieceType:
				MovableSet.append((x+i, y))
				break
			else:
				break
			i = i+1
		j = 1
		while y-j >= 0:
			if board[x][y-j] == EMPTY:
				MovableSet.append((x, y-j))
			elif getPieceType(board, (x, y-j)) != sourcePieceType:
				MovableSet.append((x, y-j))
				break
			else:
				break
			j=j+1
		j = 1
		while y+j < BOARDWIDTH:
			if board[x][y+j] == EMPTY:
				MovableSet.append((x, y+j))
			elif getPieceType(board, (x, y+j)) != sourcePieceType:
				MovableSet.append((x, y+j))
				break
			else:
				break
			j = j+1
	if piece == 'B':
		i = 1
		while x+i < BOARDWIDTH and y+i < BOARDHEIGHT:
			if board[x+i][y+i] == EMPTY:
				MovableSet.append((x+i, y+i))
			elif getPieceType(board, (x+i, y+i)) != sourcePieceType:
				MovableSet.append((x+i, y+i))
				break
			else:
				break
			i = i+1
		i = 1
		while x+i < BOARDWIDTH and y-i >= 0:
			if board[x+i][y-i] == EMPTY:
				MovableSet.append((x+i, y-i))
			elif getPieceType(board, (x+i, y-i)) != sourcePieceType:
				MovableSet.append((x+i, y-i))
				break
			else:
				break
			i = i+1
		i = 1
		while x-i >= 0 and y-i >= 0: 
			if board[x-i][y-i] == EMPTY:
				MovableSet.append((x-i, y-i))
			elif getPieceType(board, (x-i, y-i)) != sourcePieceType:
				MovableSet.append((x-i, y-i))
				break
			else:
				break
			i = i+1
		i = 1
		while x-i >= 0 and y+i < BOARDHEIGHT:
			if board[x-i][y+i] == EMPTY:
				MovableSet.append((x-i, y+i))
			elif getPieceType(board, (x-i, y+i)) != sourcePieceType:
				MovableSet.append((x-i, y+i))
				break
			else:
				break
			i = i+1
	if piece == 'N':
		i = 2
		j = 1
		if x+i < BOARDWIDTH and y-j >= 0:
			if board[x+i][y-j] == EMPTY or getPieceType(board, (x+i, y-j)) != sourcePieceType:
				MovableSet.append((x+i, y-j))
		if x+i < BOARDWIDTH and y+j < BOARDHEIGHT:
			if board[x+i][y+j] == EMPTY or getPieceType(board, (x+i, y+j)) != sourcePieceType:
				MovableSet.append((x+i, y+j))
		if x-i >= 0 and y-j >= 0:
			if board[x-i][y-j] == EMPTY or getPieceType(board, (x-i, y-j)) != sourcePieceType:
				MovableSet.append((x-i, y-j))
		if x-i >= 0 and y+j < BOARDHEIGHT:
			if board[x-i][y+j] == EMPTY or getPieceType(board, (x-i, y+j)) != sourcePieceType:
				MovableSet.append((x-i, y+j))
		if x+j < BOARDWIDTH and y-i >= 0:
			if board[x+j][y-i] == EMPTY or getPieceType(board, (x+j, y-i)) != sourcePieceType:
				MovableSet.append((x+j, y-i))
		if x-j >= 0 and y-i >= 0:
			if board[x-j][y-i] == EMPTY or getPieceType(board, (x-j, y-i)) != sourcePieceType:
				MovableSet.append((x-j, y-i))
		if x+j < BOARDWIDTH and y+i < BOARDHEIGHT:
			if board[x+j][y+i] == EMPTY or getPieceType(board, (x+j, y+i)) != sourcePieceType:
				MovableSet.append((x+j, y+i))
		if x-j >= 0  and y + i < BOARDHEIGHT:
			if board[x-j][y+i] == EMPTY or getPieceType(board, (x-j, y+i)) != sourcePieceType:
				MovableSet.append((x-j, y+i))
	if piece == 'Q':
		i = 1
		while x-i >= 0: 
			if board[x-i][y] == EMPTY:
				MovableSet.append((x-i, y))
			elif getPieceType(board, (x-i, y)) != sourcePieceType:
				MovableSet.append((x-i, y))
				break
			else:
				break
			i = i+1
		i = 1
		while x+i < BOARDWIDTH:
			if board[x+i][y] == EMPTY:
				MovableSet.append((x+i, y))
			elif getPieceType(board, (x+i, y)) != sourcePieceType:
				MovableSet.append((x+i, y))
				break
			else:
				break
			i = i+1
		j = 1
		while y-j >= 0:
			if board[x][y-j] == EMPTY:
				MovableSet.append((x, y-j))
			elif getPieceType(board, (x, y-j)) != sourcePieceType:
				MovableSet.append((x, y-j))
				break
			else:
				break
			j=j+1
		j = 1
		while y+j < BOARDWIDTH:
			if board[x][y+j] == EMPTY:
				MovableSet.append((x, y+j))
			elif getPieceType(board, (x, y+j)) != sourcePieceType:
				MovableSet.append((x, y+j))
				break
			else:
				break
			j = j+1
		i = 1
		while x+i < BOARDWIDTH and y+i < BOARDHEIGHT:
			if board[x+i][y+i] == EMPTY:
				MovableSet.append((x+i, y+i))
			elif getPieceType(board, (x+i, y+i)) != sourcePieceType:
				MovableSet.append((x+i, y+i))
				break
			else:
				break
			i = i+1
		i = 1
		while x+i < BOARDWIDTH and y-i >= 0:
			if board[x+i][y-i] == EMPTY:
				MovableSet.append((x+i, y-i))
			elif getPieceType(board, (x+i, y-i)) != sourcePieceType:
				MovableSet.append((x+i, y-i))
				break
			else:
				break
			i = i+1
		i = 1
		while x-i >= 0 and y-i >= 0: 
			if board[x-i][y-i] == EMPTY:
				MovableSet.append((x-i, y-i))
			elif getPieceType(board, (x-i, y-i)) != sourcePieceType:
				MovableSet.append((x-i, y-i))
				break
			else:
				break
			i = i+1
		i = 1
		while x-i >= 0 and y+i < BOARDHEIGHT:
			if board[x-i][y+i] == EMPTY:
				MovableSet.append((x-i, y+i))
			elif getPieceType(board, (x-i, y+i)) != sourcePieceType:
				MovableSet.append((x-i, y+i))
				break
			else:
				break
			i = i+1
	if piece == 'K':
		i = 1
		if x+i < BOARDWIDTH and (board[x+i][y] == EMPTY or (getPieceType(board, (x+i, y)) != sourcePieceType)):
			MovableSet.append((x+i, y))
		if x-i >= 0 and (board[x+i][y] == EMPTY or (getPieceType(board, (x-i, y)) != sourcePieceType)):
			MovableSet.append((x-i, y))
		if y+i < BOARDHEIGHT and (board[x+i][y] == EMPTY or (getPieceType(board, (x, y+i)) != sourcePieceType)):
			MovableSet.append((x, y+i))
		if y-i >= 0 and (board[x+i][y] == EMPTY or (getPieceType(board, (x, y-i)) != sourcePieceType)):
			MovableSet.append((x, y-i))
		if x+i < BOARDWIDTH and y+i < BOARDHEIGHT and (board[x+i][y+i] == EMPTY or (getPieceType(board, (x+i, y+i)) != sourcePieceType)):
			MovableSet.append((x+i,y+i))
		if x+i < BOARDWIDTH and y-i >= 0 and (board[x+i][y-i] == EMPTY or (getPieceType(board, (x+i, y-i)) != sourcePieceType)):
			MovableSet.append((x+i,y-i)) 
		if x-i >= 0 and y+i < BOARDHEIGHT and (board[x-i][y+i] == EMPTY or (getPieceType(board, (x-i, y+i)) != sourcePieceType)):
			MovableSet.append((x-i,y+i)) 
		if x-i >= 0 and y-i >= 0 and (board[x-i][y-i] == EMPTY or (getPieceType(board, (x-i, y-i)) != sourcePieceType)):
			MovableSet.append((x-i,y-i))   
	return MovableSet

if __name__ == '__main__':
	main()