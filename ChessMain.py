import pygame as p
import ChessEngine


WIDTH = HEIGHT = 512 # 400 marche aussi
DIMENSION = 8 #les dimension d'un echequier sont 8x8
SQ_SIZE = HEIGHT // DIMENSION #dimension d'un carré
MAX_FPS = 15
IMAGES = {}

# fonction qui permet de charger les images des différentes pièces
def loadImages():
    pieces = ["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK"]
    for i in pieces:
        IMAGES[i] = p.transform.scale(p.image.load(f"images/{i}.png"), (SQ_SIZE, SQ_SIZE))


# fonction principal qui appelle les différentes fonctions pour les taches (dessiner piece,)
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT)) #mettre l'écran par les dimensions
    clock = p.time.Clock()
    screen.fill(p.Color("green")) #couleur de l'écran
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #variable pour savoir si un mouvement est fait

    loadImages()
    running = True
    sqSelected = () # no square is selected, keep track of the last click of the user tuple(row,col)
    playerClicks = [] # garde trace des clique du joueur (2 tuple : [(7,4), (4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT: #si on appuie sur quitter
                running = False #eteindre la session
            elif e.type == p.MOUSEBUTTONDOWN:  # si on appuie sur clic droit
                location = p.mouse.get_pos() #(x,y) location og mouse
                col = location[0] // SQ_SIZE # déterminer la colonne précise ou la souris se situe
                row = location [1] // SQ_SIZE  # déterminer la ligne précise ou la souris se situe
                if sqSelected == (row, col): #the user clicked the same square
                    sqSelected = () # efface le carre selectionne
                    playerClicks = [] #effacer les clique du joueur
                else:
                    sqSelected = (row, col) # sinon prendre les nouvelle cordonne du nouveau carré
                    playerClicks.append(sqSelected) #l'ajouter au clicque du joueur
                if len(playerClicks) == 2: #si la taille du clique du joueur est égale a 2, alors :
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board) # mettre la premiere piece a l'endroit de la deuxieme sur le tableau
                    print(move.getChessNotation()) # mettre les notations de mouvements
                    if move in validMoves:
                        gs.makeMove(move)# bouger les pieces
                        moveMade = True
                    sqSelected = () #reset
                    playerClicks = [] #reset

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undoMove() #appelle la fonction 
                    moveMade = True #le move a ete fait

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen,gs)
        clock.tick(MAX_FPS)
        p.display.flip()

# Fonction qui dessine les différentes partie de l'échequier
def drawGameState(screen,gs):
    drawBoard(screen) # dessine carré sur l'échequier
    drawPieces(screen,gs.board) # dessine les piece


# dessine l'échequier avec une case sur 2 gris puis blanc
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]

    font = p.font.SysFont('Arial', 24, bold=True)
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color= colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

                        # Ajouter les numéros horizontaux de droite à gauche (en haut)
            if row == 0:
                number_text = font.render(str(1 + column), True, p.Color("green"))
                screen.blit(number_text, (column * SQ_SIZE + 5, 5))

            # Ajouter les numéros verticaux de haut en bas (à gauche)
            if column == 0:
                number_text = font.render(str(1 + row), True, p.Color("green"))
                screen.blit(number_text, (5, row * SQ_SIZE + 5))


# fonction qui dessine les pieces
def drawPieces(screen,board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main() 
