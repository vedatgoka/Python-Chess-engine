class GameState():
    def __init__(self):
        # le tableau est en dimension 8x8. C'est aussi la représentation de l'échéquier au départ
        #  Le premier caractère représente la couleur,
        # w = white, b = black
        # R = tour, N = chevalier, B = fou, Q = reine, K = roi
        # les "--" représente des espaces vide 
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--", "--", "wp", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "wK", "--", "--", "--", "--"], 
            ["--", "--", "bp", "--", "--", "--", "--", "--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N" :self.getKnightMoves,
                            "B": self.getBishopMoves, "Q" : self.getQueenMoves, "K" : self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []





    # prend un mouvement et l'execute (ne marche pas pour la promotion du pion et en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it  later
        self.whiteToMove = not self.whiteToMove #swap players

    #le dernier mouvement executé
    def undoMove(self):
        if len(self.moveLog) != 0: #si un coup a ete enregistré
            move = self.moveLog.pop() #revenir en arriere
            self.board[move.startRow][move.startCol] = move.pieceMoved 
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #change de joueur


    # fonction qui considere si un mouvement met le roi en echecs

    def getValidMoves(self):
        return self.getAllPossibleMoves()

    #tous les autres mouvements sans considere les echecs
    def getAllPossibleMoves(self):
        moves = [Move((6,4), (4,4), self.board)]
        for r in range(len(self.board)): #nombre de ligne 
            for c in range(len(self.board[r])): #nombre de colonne
                turn = self.board[r][c][0] #prend la couleur de la piece sur la ligne et colonne.
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove): #si c'est le tour au blanc
                    piece = self.board[r][c][1] #prendre la pièce
                    self.moveFunctions[piece](r,c,moves) #appelle la fonction approprié pour la piece
        return moves


    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: #verifier si blanc joue
            if self.board[r-1][c] == "--": # si la case devant le pion est vide
                moves.append(Move((r,c), (r-1,c), self.board)) # alors avancer de 1 case
                if r == 6 and self.board[r-2][c] == "--": #si le pion est sur sa ligne de départ et que 2 ligne devant il n'y a rien
                    moves.append(Move((r,c),(r-2,c), self.board)) #avance 2 deux case vers l'avant
            if c-1 >= 0: #capture a gauche
                if self.board[r-1][c-1][0] == "b": #si piece enemie est noir diagonal gauche
                    moves.append(Move((r,c),(r-1,c-1), self.board)) #manger la piece noir
            if c+1 < 7: # capture a droite
                if self.board[r-1][c+1][0] == "b": #si la piece diagonal droite est noir
                    moves.append(Move((r,c),(r-1,c+1), self.board)) # manger la piece noir
        else: #pion noir
            if self.board[r+1][c] == "--": # si la case devant le pion est vide
                moves.append(Move((r,c), (r+1,c), self.board)) # alors avancer de 1 case
                if r == 1 and self.board[r+2][c] == "--": #si le pion est sur sa ligne de départ et que 2 ligne devant il n'y a rien
                    moves.append(Move((r,c),(r+2,c), self.board)) #avance 2 deux case vers l'avant
            if c-1 >= 0: #capture a droite
                if self.board[r+1][c-1][0] == "w": #si piece enemie est noir diagonal gauche
                    moves.append(Move((r,c),(r+1,c-1), self.board)) #manger la piece noir
            if c+1 <= 7: # capture a droite
                if self.board[r+1][c+1][0] == "w": #si la piece diagonal droite est noir
                    moves.append(Move((r,c),(r+1,c+1), self.board)) # manger la piece noir

    def getRookMoves(self,r,c,moves):
        directions = ((-1,0), (0,-1), (1,0),(0,1)) #up left, down, right
        enemyColor = "b" if self.whiteToMove else "w" #si c'est le tour blanc, "b"
        for d in directions:
            for i in range(1,8):
                for i in range(1,8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getKnightMoves(self,r,c,moves):
        directions = ((-2,-1), (-2,1), (2,-1),(2,1), (1,2),(-1,2),(1,-2),(-1,-2)) #up left, down, right
        enemyColor = "b" if self.whiteToMove else "w" #si c'est le tour blanc, "b"
        for d in directions:
            for i in range(1,8):
                for i in range(1,8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getBishopMoves(self,r,c,moves):
        directions = ((-1,-1), (-1,1), (1,-1),(1,1)) # up_left , up_right, down_left, down_right
        enemyColor = "b" if self.whiteToMove else "w" #si c'est le tour blanc, "b"
        for d in directions:
            for i in range(1,8):
                for i in range(1,8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getQueenMoves(self,r,c,moves):
        directions = ((-1,0), (0,-1), (1,0),(0,1),(-1,-1), (-1,1), (1,-1),(1,1)) # up_left , up_right, down_left, down_right
        enemyColor = "b" if self.whiteToMove else "w" #si c'est le tour blanc, "b"
        for d in directions:
            for i in range(1,8):
                for i in range(1,8):
                    endRow = r + d[0] * i
                    endCol = c + d[1] * i
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break


    def getKingMoves(self,r,c,moves):
        directions = ((-1,0), (0,-1), (1,0),(0,1),(-1,-1), (-1,1), (1,-1),(1,1)) # up_left , up_right, down_left, down_right
        enemyColor = "b" if self.whiteToMove else "w" #si c'est le tour blanc, "b"
        for d in directions:
            for i in range(1,8):
                for i in range(1,8):
                    endRow = r + d[0]
                    endCol = c + d[1]
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                            break
                        else:
                            break
                    else:
                        break


    
class Move():
    #maps keys to values
    # key : value

    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
 
    rowsToRanks = {v: k for k,v in ranksToRows.items()}

    filesToCols = {"a":0, "b":1,"c":2,"d":3,
                    "e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v : k for k, v in filesToCols.items()}





    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
