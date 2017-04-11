Spring 2016 Python Project
Author - Anshul Doshi
UNI - ad3222
Partners: None - solo-project

Building Chess using Pygame

Usage:
type to run:
pythonw main.py

Motivation:
This class was my first introduction to python. Since we had covered so many different areas in which python can be useful in class, I was really excited in trying my hand with truly exploring what python can do. With the stress of finals, I thought this project was a great way to do something fun such as make a game. Since I love playing chess, and I often go on chess.com and play online in my free time, I thought it would be a cool idea to simulate a 2 player chess game using pygame. In my head, it seemed straightforward theoretically to implement since I was so familiar with the game, but as I got down to it, I realized the task is much more challenging than I initially thought. In any case, I stuck with it to the best of my ability and came-up with a semi-working playable game. Although there are a few rules missing, such as castling and enpassant and pawn promotion, there is still a great deal of logic involved in getting the game to function on its basic principles. This project was a great learning experience for me and has been a fascinating journey in learning the inner workings of pygame.

Modules:
the only module I used was pygame with I installed by follwoing the directions laid out by the TA on piazza. Even after using homebrew and the like, the installation of pygame was still done using pip. 

Rundown:
In order to implement this chess game, I took the task in 3 steps. 

	1. Draw the board. 
		-   the first step of the program is to set up the game of course, calling pygame.init() etc... but after the, the first real task is creating a board. First 
			I loaded all my chess icon images and then I created the squares necessary to make a 8x8 board. The next step was filling those squares with alternating colors so it really looks like a chess board. Lastly, we put all the images in their respective starting position of the chess board.
	2. Making valid moves and the board data structure
		-   Once we have the board, we need to detect for mouse clicks and determine whether the moves being made are valid. In order to do this, quite a number of 	functions are implemented. First off, we check the easy cases, the user selected a piece of the right color, the move is on the board etc... Then we must
			discern whether a move for each specific piece is valid. Thus, the program uses a large function called getMovableSet which basically uses the board data structure in order to return a list of a set of coordinates that a piece at a specific location can go to. The reason the function is so long is becuase it must detect whether pieces are blocking it and whether it can capture enemy pieces. Thus, if the target location is in a pieces movable set, we can make the move
	3. Making the move, reversing the board and checks/checkmate
		-	Lastly, we make the move, update our data structure to reflect the move and redraw the board. If we captured a piece, we keep a mini-captured pieces data
			structure that draws the piece in the captured pieces box off to the side. Next, we reverse the board an allow the second player to go. Lastly, we must check for checks and checkmate. This was the most challenging part for me and after hours of trying, there were still too many issues with my check function. I was able to comete a check detecting function that screams check when a player is in check. Then when I tried to restrict the moves the perosn in check can make, I ran into many problems. My implementation, creates a new board, and simulates a move that a person want to make. By finding our king location in the new board and taking the movableset of the checking piece, if the king is still in check after the move, the move is invalid. Hoever, when trying to implement this, the logic seems off as it leads to random captures and inavlid moves. Since I couldnt implemtn check, i couldnt do checkmate either but, in theory it would be a function that returns true if there are no moves that make check reutrn false.

Challenges:
As i already mentioned, I faced many challenges with the check function and after many hours of struggling with it, I still had no luck. The main challenge throughout this process was coming up with the board data structure. Initially I had a regular 2-d array holding images, but as I realized we need more and more information, I kept adding, making it a 2d array of lists with piece type, color etc... I ran into quite a few issues in creating the board, especially coming up with the alternating logic but I was able to draw it out and list different indeces to find a pattern. Lastly, the largest challenge throughout this whole process was the reversal of the board and how that impacted the different indices. Once i figured out the reversal logic, I kept running into problems in which the reversal was impacting different functions. It was very difficult to debug but once I laid enough print statements inside the code, I was able to figure out what was going on. 