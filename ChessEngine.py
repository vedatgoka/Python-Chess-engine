
"""
Cette classe est responsable de stocker toutes les informations sur l'état actuel d'une partie d'échecs. 
Elle valide les mouvements valides et conserve un journal des coups.
"""

class GameState:
    def __init__(self):
        """
        Board is a 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        self.whiteKingLocation = (7, 4) #position du roi blanc
        self.blackKingLocation = (0, 4) #position du roi noir
        self.enpassantPossible = () #stocke une case ou un coup en passant est possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.whiteToMove = True #tour des blanc
        self.checkmate = False #si c'est un echec et mat
        self.stalemate = False #si c'est un echec
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.moveLog = [] #liste des coups joués

    """
    Applique un mouvement sur l'échiquier, en mettant à jour les variables liées à l'état du jeu.
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"  # Vide la case de départ
        self.board[move.endRow][move.endCol] = move.pieceMoved  # Place la pièce sur la case d'arrivée
        self.moveLog.append(move)  # Ajoute le mouvement au journal
        self.whiteToMove = not self.whiteToMove  # Change le tour

        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)  # Met à jour la position du roi blanc
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)  # Met à jour la position du roi noir

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q' #Promotion automatique des pions en reines.

        # if enpassant move, capture pawn
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' 
            #Gère les captures en passant.

        # Définit si un coup en passant est possible après un déplacement de pion de deux cases.
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # only on 2-square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # make castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # move the rook
                self.board[move.endRow][move.endCol + 1] = '--'  # erase old rook
            else:  # queen side
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible)  # Sauvegarde l'état du coup en passant
        self.updateCastleRights(move)  # Met à jour les droits de roque
        self.castleRightsLog.append(CastleRights(
            self.currentCastlingRight.wks, self.currentCastlingRight.bks,
            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    """
    Undo the last move
    """
    def undoMove(self):
        if len(self.moveLog) != 0:  # Vérifie si des coups ont été joués
            move = self.moveLog.pop()  # Récupère le dernier mouvement
            self.board[move.startRow][move.startCol] = move.pieceMoved  # Replace la pièce déplacée
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # Replace la pièce capturée (ou "--" si aucune)
            self.whiteToMove = not self.whiteToMove  # Change le tour

            # update king's position
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:  # Gère l'annulation des captures en passant
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enpassantPossibleLog.pop()  # Supprime l'état en passant actuel
            self.enpassantPossible = self.enpassantPossibleLog[-1]  # Rétablit le précédent

            self.castleRightsLog.pop()  # Supprime l'état actuel des droits de roque
            self.currentCastlingRight = CastleRights(
                self.castleRightsLog[-1].wks, self.castleRightsLog[-1].bks,
                self.castleRightsLog[-1].wqs, self.castleRightsLog[-1].bqs)

            # undo castle move
            if move.isCastleMove: #annule les mouvements de roque
                if move.endCol - move.startCol == 2:  # king side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            # undo possible game over
            self.checkmate = False # Réinitialise l'état de fin de partie
            self.stalemate = False

    """
    All moves, considering checks.
    1. Generates all possible moves
    2. For each move, makes the move
    3. Generates all opponent's moves
    4. For each opponent move, check if your king is attacked
    """
    def getValidMoves(self):
        tempEnpassantePossible = self.enpassantPossible # Sauvegarde l'état actuel
        tempCurrentCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                               self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPossibleMoves() # Récupère tous les mouvements possibles

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):  # Parcourt les mouvements en sens inverse
            self.makeMove(moves[i])  # Simule chaque mouvement
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():  # Supprime les mouvements qui laissent le roi en échec
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()  # Annule le mouvement simulé


        if len(moves) == 0:  # Vérifie si aucun mouvement n'est possible
            if self.inCheck():
                self.checkmate = True  # Si le joueur est en échec, c'est un mat
            else:
                self.stalemate = True  # Sinon, c'est un pat
        else:
            self.checkmate = False
            self.stalemate = False


        self.enpassantPossible = tempEnpassantePossible  # Restaure l'état initial
        self.currentCastlingRight = tempCurrentCastleRights
        return moves #retourne la liste de mouvements valides

    """
    Determines if the current player is in check
    """
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determines if the enemy can attack square at row and column
    """
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # Simule le tour de l'adversaire
        oppMoves = self.getAllPossibleMoves()  # Récupère tous ses mouvements
        self.whiteToMove = not self.whiteToMove

        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True  # Si une pièce adverse peut atteindre cette case, elle est attaquée

        return False


    """
    All moves without considering checks
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # Détermine la couleur de la pièce
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]  # Identifie le type de la pièce
                    self.moveFunctions[piece](r, c, moves)  # Appelle la fonction associée
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add moves to the list
    """
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":  # vérifie si 1 case devant est vide
                moves.append(Move((r, c), (r - 1, c), self.board))#avance d'une case
                if r == 6 and self.board[r - 2][c] == "--":  #  vérifie si 2 case devant est vide
                    moves.append(Move((r, c), (r - 2, c), self.board))#avance de 2 case
            if c - 1 >= 0:  # left capture
                if self.board[r - 1][c - 1][0] == "b": #regarde si c'est une piece noire
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:  # left enpassante
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # right capture
                if self.board[r - 1][c + 1][0] == "b": #regarde si c'est une piece noir
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:  # right enpassante
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # right capture
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:  # right enpassante
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # left capture
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:  # left enpassante
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    """
    Get all the rook moves for the rook located at row, col and add moves to the list
    """
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Haut, gauche, bas, droite
        enemyColor = "b" if self.whiteToMove else "w"  # Couleur de l'adversaire

        for direction in directions:
            for i in range(1, 8):  # Une tour peut se déplacer jusqu'à 7 cases
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Reste dans les limites de l'échiquier
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Case vide
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Capture une pièce ennemie
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Une pièce alliée bloque le chemin
                        break
                else:
                    break


    """
    Get all the knight moves for the knight located at row, col and add moves to the list
    """
    def getKnightMoves(self, r, c, moves):
        directions = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        allyColor = "w" if self.whiteToMove else "b"  # Couleur alliée

        for move in directions:
            endRow = r + move[0]
            endCol = c + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # Vérifie les limites
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Peut capturer une pièce ennemie ou se déplacer sur une case vide
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get all the bishop moves for the bishop located at row, col and add moves to the list
    """
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemyColor = "b" if self.whiteToMove else "w"

        for direction in directions:
            for i in range(1, 8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i

                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # check if the move is on board
                    endPiece = self.board[endRow][endCol]

                    if endPiece == "--":  # empty space is valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    """
    Get all the queen moves for the queen located at row, col and add moves to the list
    """
    def getQueenMoves(self, r, c, moves):
        #mouvement du fou + tour
        self.getBishopMoves(r, c, moves) 
        self.getRookMoves(r, c, moves)

    """
    Get all the king moves for the king located at row, col and add moves to the list
    """
    def getKingMoves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
        allyColor = "w" if self.whiteToMove else "b"

        for move in king_moves:
            endRow = r + move[0]
            endCol = c + move[1]

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #déplacement si différent de la couleur du roi
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Update the castle rights given the move
    """
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # right rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # left rook
                    self.currentCastlingRight.bks = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                    self.currentCastlingRight.qks = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    """
    Generate all valid castle moves for the king at (r, c) and add them to the list
    """

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # Roque côté roi pour les blancs
        self.bks = bks  # Roque côté roi pour les noirs
        self.wqs = wqs  # Roque côté dame pour les blancs
        self.bqs = bqs  # Roque côté dame pour les noirs

class Move:
    """
    In chess, fields on the board are described by two symbols, one of them being number between 1-8 (which is corresponding to rows)
    and the second one being a letter between a-f (corresponding to columns), in order to use this notation we need to map our [row][col] coordinates
    to match the ones used in the original chess game
    """
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        self.isCastleMove = isCastleMove

        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.isCapture = self.pieceCaptured != "--"

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    """
    Overriding the string function
    """
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
