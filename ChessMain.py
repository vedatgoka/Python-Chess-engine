"""
This is the main driver file. 
It is responsible for handling user input and displaying the current game state
"""

import pygame as p
import ChessEngine
import ChessAI
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Dimensions d'un échiquier : 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION  # Taille d'une case de l'échiquier
MAX_FPS = 15  # Taux de rafraîchissement pour les animations
IMAGES = {}  # Dictionnaire pour stocker les images des pièces
COLORS = [p.Color("white"), p.Color("gray")]  # Couleurs des cases de l'échiquier


"""
Initialize global dictionary of images. 
This will be called exactly once in the main function
"""
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
The main driver for the code. 
It will handle user input and updating the graphics
"""
def main():
    p.init()  # Initialise Pygame
    p.mixer.init()  # Initialise le système audio de Pygame
    screen = p.display.set_mode([BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT])  # Crée la fenêtre du jeu
    clock = p.time.Clock()  # Gère le temps pour les animations
    moveLogFont = p.font.SysFont("Arial", 14, False, False)  # Police utilisée pour afficher les coups joués
    gs = ChessEngine.GameState()  # Initialise l'état du jeu
    validMoves = gs.getValidMoves()  # Liste des mouvements valides initiaux
    sqSelected = ()  # Dernière case cliquée par l'utilisateur (ligne, colonne)
    playerClicks = []  # Liste des clics de l'utilisateur : [(départ), (arrivée)]
    playerOne = True  # Indique si le joueur humain joue avec les blancs
    playerTwo = False  # Indique si un joueur humain joue avec les noirs
    moveFinderProcess = None  # Processus pour rechercher le meilleur coup de l'IA
    returnQueue = None  # File pour la communication entre le processus principal et l'IA
    AIThinking = False  # Indique si l'IA est en train de réfléchir
    gameOver = False  # Indique si la partie est terminée
    moveMade = False  # Indique si un coup a été joué
    moveUndone = False  # Indique si un coup a été annulé
    animate = False  # Indique si une animation de déplacement est en cours
    running = True  # Contrôle la boucle principale


    loadImages() # Charge les images des pièces dans le dictionnaire global IMAGES

    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo) 
        #vérifie si c'est le tour d'un humain de jouer, en fonction de la couleur et des joueurs.

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:  # Gère les clics de souris
                if not gameOver:
                    location = p.mouse.get_pos()  # Coordonnées de la souris
                    col = location[0] // SQ_SIZE  # Colonne cliquée
                    row = location[1] // SQ_SIZE  # Ligne cliquée

                    if sqSelected == (row, col) or col >= 8:  # Annule la sélection si le clic est redondant
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)  # Stocke la case sélectionnée
                        playerClicks.append(sqSelected)  # Ajoute la case à la liste des clics

                    if len(playerClicks) == 2 and isHumanTurn:  # Si deux clics (un coup complet)
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):  # Vérifie si le coup est valide
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])  # Applique le coup
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:  # Si le coup n'est pas valide
                            playerClicks = [sqSelected]


            elif e.type == p.KEYDOWN:  # Gère les entrées clavier
                if e.key == p.K_u:  # Touche 'u' pour annuler un coup
                    gs.undoMove()  # Annule le dernier coup
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()  # Arrête le processus de l'IA si nécessaire
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:  # Touche 'r' pour redémarrer la partie
                    gs = ChessEngine.GameState()  # Réinitialise l'état du jeu
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True


        if not gameOver and not isHumanTurn and not moveUndone:  # Tour de l'IA
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # File pour récupérer le coup de l'IA
                moveFinderProcess = Process(target=ChessAI.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()  # Lance le processus de l'IA

            if not moveFinderProcess.is_alive():  # Si l'IA a terminé
                AIMove = returnQueue.get()  # Récupère le coup choisi par l'IA
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(validMoves)  # Coup aléatoire si aucun coup optimal trouvé
                gs.makeMove(AIMove)  # Joue le coup
                moveMade = True
                animate = True
                AIThinking = False


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)  # Anime le dernier coup
            validMoves = gs.getValidMoves()  # Met à jour les mouvements valides
            moveMade = False
            animate = False
            moveUndone = False


        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)  # Affiche l'état actuel du jeu

        if gs.checkmate or gs.stalemate:  # Vérifie si la partie est terminée
            gameOver = True
            if gs.stalemate:
                text = "Stalemate"  # Partie nulle
            else:
                text = "Black wins by checkmate" if gs.whiteToMove else "White wins by checkmate"
            drawEndGameText(screen, text)  # Affiche un message de fin de partie

        clock.tick(MAX_FPS)  # Contrôle le taux de rafraîchissement
        p.display.flip()  # Met à jour l'affichage



"""
Responsible for all the graphics within a current game state
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)


"""
Draws the squares on the board.
In chess, the top left square is always light.
"""
def drawBoard(screen):
    global COLORS
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Highlight square selection
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # highlight valid moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


"""
Draws the pieces on top of the board using the current GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]

            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draws the move log on the right side of the window
"""
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):  # append opponent move
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 2
    padding = 5
    lineSpacing = 2
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]

        textObject = font.render(text, True, p.Color('White'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


"""
Animating a move including playing the sound
"""
def animateMove(move, screen, board, clock):
    if move.isCapture:
        p.mixer.music.load("audio/capture.mp3")
        p.mixer.music.play()
    else:
        p.mixer.music.load("audio/move.mp3")
        p.mixer.music.play()

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(60)


"""
Draw text on screen
"""
def drawEndGameText(screen, text):
    # Draw text shadow
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

    # Draw main text
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
