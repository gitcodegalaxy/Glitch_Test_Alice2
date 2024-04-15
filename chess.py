'''

Chess 2 Player (1/22/2017)


Piece symbols:
  Pawn   - ♟
  King   - ♚
  Queen  - ♛
  Knight - ♞
  Bishop - ♝
  Rook   - ♜

'''

import time
from processing import *

FRAMERATE = 100
DELTATIME = 1 / FRAMERATE

SCREENSIZE = 640
HALFSCREENSIZE = SCREENSIZE // 2
UIHEIGHT = SCREENSIZE // 6
SQUARESIZE = SCREENSIZE // 8
HALFSQUARESIZE = SQUARESIZE // 2

turn = "white"

images = {
  "pawn"  : "♟",
  "king"  : "♚",
  "queen" : "♛",
  "knight": "♞",
  "bishop": "♝",
  "rook"  : "♜"
}

class Board:
  
  def __init__(self):
    self.squares = [[Piece(Pos(j, i), None, None) for j in xrange(8)] for i in xrange(8)]
    self.selectedPiece = None
  
  def isEmpty(self, x, y):
    if self.squares[int(y)][int(x)].name == None:
      return True
    return False
  def pieceAt(self, x, y):
    return self.squares[int(y)][int(x)]
  def setPieceAt(self, x, y, newPiece):
    self.squares[int(y)][int(x)] = newPiece
  def movePiece(self, currentPos, newPos):
    piece = self.pieceAt(currentPos.x, currentPos.y)
    self.setPieceAt(currentPos.x, currentPos.y, Piece(currentPos, None, None))
    self.setPieceAt(newPos.x, newPos.y, piece)
    piece.pos = newPos
  def findKing(self, side):
    for row in xrange(8):
      for col in xrange(8):
        if self.pieceAt(col, row).name == "king":
          if self.pieceAt(col, row).side == side:
            return Pos(col, row)
  
  def displayBoard(self):
    isBlack = False
    for i in xrange(8):
      for j in xrange(8):
        if isBlack:
          fill(105, 90, 75)
        else:
          fill(170, 155, 130)
        isBlack = not isBlack
        rect(j * SQUARESIZE, i * SQUARESIZE, SQUARESIZE, SQUARESIZE)
      isBlack = not isBlack
      
  def updatePieces(self):
    self.displayPieces()
    self.updateSelectedPiece()
  
  def displayPieces(self):
    for row in xrange(len(self.squares)):
      for col in xrange(len(self.squares[row])):
        piece = self.squares[row][col]
        if not piece.name:
          # empty square
          continue
        if piece.side == "white":
          fill(200)
        else:
          fill(0)
        textAlign(CENTER, CENTER)
        textSize(SQUARESIZE)
        text(images[piece.name], col * SQUARESIZE + HALFSQUARESIZE, row * SQUARESIZE + HALFSQUARESIZE)
  
  def updateSelectedPiece(self):
    if self.selectedPiece:
      moves = self.selectedPiece.moves(self)
      for movePos in moves:
        # Draw fill red for taking a piece.
        if self.squares[movePos.y][movePos.x].name != None:
          fill(220, 0, 0)
        else:
          fill(220)
        ellipse(movePos.x * SQUARESIZE + HALFSQUARESIZE, movePos.y * SQUARESIZE + HALFSQUARESIZE, SQUARESIZE / 6, SQUARESIZE / 6)
  
  def click(self, x, y):
    if y > SCREENSIZE:
      # UI
      if ui.state == "promotion":
        promotionChoice = ui.promotionChoice(x, y)
        if promotionChoice != None:
          # Reset the UI state and replace the pawn with the knight or queen.
          ui.state = "information"
          pos = self.selectedPiece.pos
          if promotionChoice == "queen":
            self.squares[pos.y][pos.x] = Queen(pos, self.selectedPiece.side)
          else:
            self.squares[pos.y][pos.x] = Knight(pos, self.selectedPiece.side)
    else:
      # Board
      global turn
      tileX = int(x // SQUARESIZE)
      tileY = int(y // SQUARESIZE)
      if self.selectedPiece:
        # Check if this is a legal move.
        moves = self.selectedPiece.moves(self)
        legal = False
        movePos = Pos(tileX, tileY)
        # Compare the moveto the generated list of legal moves for that piece.
        for legalMovePos in moves:
          if movePos.x == legalMovePos.x and movePos.y == legalMovePos.y:
            legal = True
        if legal:
          # Change whose turn it is
          if turn == "white":
            turn = "black"
          else:
            turn = "white"
          # 2 steps to moving: remove the piece from it's current square, then set the new square to that piece.
          # If a piece is already there, it will be overridden, killing it.
          selectedPos = self.selectedPiece.pos
          if self.squares[tileY][tileX].name != None:
            # We're killing a piece, so add it to UI's captured pieces list.
            piece = self.squares[tileY][tileX]
            if piece.side == "white":
              # Add to the list opposite of the side that piece is on: the capturing side.
              ui.takenPieces["black"].append(images[piece.name])
            else:
              ui.takenPieces["white"].append(images[piece.name])
          kingMoved = False
          self.movePiece(selectedPos, Pos(tileX, tileY))
          if self.selectedPiece.name == "king" or self.selectedPiece.name == "rook":
            # A piece can't castle if it has moved.
            if self.selectedPiece.name == "king" and self.selectedPiece.canCastle:
              kingMoved = True
            self.selectedPiece.canCastle = False
          if kingMoved:
            # Check if the player did just castle. If so, move the rook over.
            if tileX == 1:
              self.movePiece(Pos(0, selectedPos.y), Pos(2, selectedPos.y))
            if tileX == 5:
              self.movePiece(Pos(7, selectedPos.y), Pos(4, selectedPos.y))
          # Check if a pawn needs promotion:
          if self.selectedPiece.name == "pawn":
            if self.selectedPiece.needsPromotion():
              # Let the player decide to promote to a queen or knight.
              ui.state = "promotion"
              # Keep the pawn as the selected piece, temporarily.
              return
        if ui.state != "promotion":
          # Only reset selected piece if a player isn't choosing how to promote a pawn, as selectedPiece is used in the process.
          self.selectedPiece = None
      else:
        # Set a new selected piece, unless the square is empty or it's the other color's piece.
        piece = self.pieceAt(tileX, tileY)
        if piece.name and piece.side == turn:
          self.selectedPiece = piece
  
  def safe(self, x, y, side):
    # Check if a square (x, y) is being attacked by a side.
    # To do this, we see which pieces a hypothetical queen could attack from that square,
    # and check if that square can indeed attack the position the hypothetical queen is at.
    # Do the same for knights.
    hQueen = Queen(Pos(x, y), side)
    hKnight = Knight(Pos(x, y), side)
    hMovesQ = hQueen.attacks(self)
    hMovesK = hKnight.attacks(self)
    hAttacking = []
    for move in hMovesQ:
      if not self.isEmpty(move.x, move.y):
        hAttacking.append(self.pieceAt(move.x, move.y))
    for move in hMovesK:
      if not self.isEmpty(move.x, move.y):
        # For knights, only append the piece if it's another knight.
        if self.pieceAt(move.x, move.y).name == "knight":
          hAttacking.append(self.pieceAt(move.x, move.y))
    # Check attacking moves to see if they attack back (rook on a diagonal doesn't, a bishop would).
    hThreats = []
    for attacker in hAttacking:
      for attack in attacker.attacks(self):
        hThreats.append(attack)
    # Check if any of the threatened squares are the square we're checking.
    for threat in hThreats:
      if threat.x == x and threat.y == y:
        # The square is being threatened.
        return False
    # No Threats.
    return True
  
  def keepsKingSafe(self, currentPos, newPos):
    piece = self.pieceAt(currentPos.x, currentPos.y)
    hBoard = Board()
    for row in xrange(len(self.squares)):
      for col in xrange(len(self.squares[row])):
        hBoard.squares[row][col] = self.squares[row][col]
    hBoard.squares[currentPos.y][currentPos.x] = Piece(Pos(currentPos.x, currentPos.y), None, None)
    hBoard.squares[newPos.y][newPos.x] = piece
    kingPos = hBoard.findKing(piece.side)
    if hBoard.safe(kingPos.x, kingPos.y, piece.side):
      return True
    else:
      return False


class Pos:
  def __init__(self, x, y):
    self.x = x
    self.y = y
  
  def __str__(self):
    return "(%s, %s)" %(self.x, self.y)

class Piece:
  def __init__(self, pos, name, side):
    self.pos = pos
    self.name = name
    self.side = side

'''
All pieces:
'''
class Pawn(Piece):
  def __init__(self, pos, side):
    Piece.__init__(self, pos, "pawn", side)
  
  def needsPromotion(self):
    # Have we reached the end of the board?
    if self.side == "white":
      if self.pos.y == 7:
        return True
    else:
      if self.pos.y == 0:
        return True
    return False
  
  def moves(self, hBoard):
    # Return an array of valid moves for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    if self.side == "white":
      # Forwards
      if self.pos.y != 7:
        if squares[self.pos.y + 1][self.pos.x].name == None:
          # Be sure the square's emtpy
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y + 1)):
            legalMoves.append(Pos(self.pos.x, self.pos.y + 1))
          # Check if moving 2 up is valid (first move for the pawn)
          if self.pos.y == 1:
            if squares[self.pos.y + 2][self.pos.x].name == None:
              if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y + 2)):
                legalMoves.append(Pos(self.pos.x, self.pos.y + 2))
        # Attack
        if self.pos.x != 0:
          if squares[self.pos.y + 1][self.pos.x - 1].name != None:
            if squares[self.pos.y + 1][self.pos.x - 1].side != self.side:
              if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - 1, self.pos.y + 1)):
                legalMoves.append(Pos(self.pos.x - 1, self.pos.y + 1))
        if self.pos.x != 7:
          if squares[self.pos.y + 1][self.pos.x + 1].name != None:
            if squares[self.pos.y + 1][self.pos.x + 1].side != self.side:
              if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + 1, self.pos.y + 1)):
                legalMoves.append(Pos(self.pos.x + 1, self.pos.y + 1))
    else:
      # Forwards
      if self.pos.y != 0:
        if squares[self.pos.y - 1][self.pos.x].name == None:
          # Be sure the square's emtpy
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y - 1)):
            legalMoves.append(Pos(self.pos.x, self.pos.y - 1))
          # Check if moving 2 up is valid (first move for the pawn)
          if self.pos.y == 6:
            if squares[self.pos.y - 2][self.pos.x].name == None:
              if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y - 2)):
                legalMoves.append(Pos(self.pos.x, self.pos.y - 2))
        # Attack
        if self.pos.x != 0:
          if squares[self.pos.y - 1][self.pos.x - 1].name != None:
            if hBoard.squares[self.pos.y - 1][self.pos.x - 1].side != self.side:
              if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - 1, self.pos.y - 1)):
                legalMoves.append(Pos(self.pos.x - 1, self.pos.y - 1))
        if self.pos.x != 7:
          if squares[self.pos.y - 1][self.pos.x + 1].name != None:
            if squares[self.pos.y - 1][self.pos.x + 1].side != self.side:
              if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + 1, self.pos.y - 1)):
                legalMoves.append(Pos(self.pos.x + 1, self.pos.y - 1))
    
    return legalMoves
  
  def attacks(self, hBoard):
    # Return an array of valid attacks for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    if self.side == "white":
      # Forwards
      if self.pos.y != 7:
        # Attack
        if self.pos.x != 0:
          if squares[self.pos.y + 1][self.pos.x - 1].side != self.side:
            legalMoves.append(Pos(self.pos.x - 1, self.pos.y + 1))
        if self.pos.x != 7:
          if squares[self.pos.y + 1][self.pos.x + 1].side != self.side:
            legalMoves.append(Pos(self.pos.x + 1, self.pos.y + 1))
    else:
      if self.pos.y != 0:
        # Attack
        if self.pos.x != 0:
          if hBoard.squares[self.pos.y - 1][self.pos.x - 1].side != self.side:
            legalMoves.append(Pos(self.pos.x - 1, self.pos.y - 1))
        if self.pos.x != 7:
          if squares[self.pos.y - 1][self.pos.x + 1].side != self.side:
            legalMoves.append(Pos(self.pos.x + 1, self.pos.y - 1))
    
    return legalMoves
class King(Piece):
  def __init__(self, pos, side):
    Piece.__init__(self, pos, "king", side)
    self.canCastle = True
  
  def castling(self, hBoard):
    legalCastle = []
    
    if self.canCastle:
      # Kingside
      if hBoard.isEmpty(self.pos.x - 1, self.pos.y) and hBoard.isEmpty(self.pos.x - 2, self.pos.y):
        if hBoard.pieceAt(self.pos.x - 3, self.pos.y).name == "rook":
          if hBoard.pieceAt(self.pos.x - 3, self.pos.y).canCastle:
            if hBoard.safe(self.pos.x, self.pos.y, self.side) and hBoard.safe(self.pos.x - 1, self.pos.y, self.side) and hBoard.safe(self.pos.x - 2, self.pos.y, self.side):
              legalCastle.append(Pos(self.pos.x - 2, self.pos.y))
      # Queenside
      if hBoard.isEmpty(self.pos.x + 1, self.pos.y) and hBoard.isEmpty(self.pos.x + 2, self.pos.y) and hBoard.isEmpty(self.pos.x + 3, self.pos.y):
        if hBoard.pieceAt(self.pos.x + 4, self.pos.y).name == "rook":
          if hBoard.pieceAt(self.pos.x + 4, self.pos.y).canCastle:
            if hBoard.safe(self.pos.x, self.pos.y, self.side) and hBoard.safe(self.pos.x + 1, self.pos.y, self.side) and hBoard.safe(self.pos.x + 2, self.pos.y, self.side):
              legalCastle.append(Pos(self.pos.x + 2, self.pos.y))
    
    return legalCastle
  
  def moves(self, hBoard):
    # Return an array of valid moves for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    for i in xrange(-1, 2):
      for j in xrange(-1, 2):
        if i == 0 and j == 0:
          # Moving to himself isn't legal
          continue
        if self.pos.x + j <= 7 and self.pos.x + j >= 0 and self.pos.y + i <= 7 and self.pos.y + i >= 0:
          # Don't take pieces from its own side!
          if squares[self.pos.y + i][self.pos.x + j].side != self.side:
            # Now we check if this move will put the king in check.
            # Create a hypothetical hBoard where the king is there and check if the square is safe or not.
            if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + j, self.pos.y + i)):
              legalMoves.append(Pos(self.pos.x + j, self.pos.y + i))
    
    # Check castling.
    for move in self.castling(hBoard):
      legalMoves.append(move)
    
    return legalMoves
  
  def attacks(self, hBoard):
    # Return an array of valid attacks for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    for i in xrange(-1, 2):
      for j in xrange(-1, 2):
        if i == 0 and j == 0:
          # Moving to himself isn't legal
          continue
        if self.pos.x + j <= 7 and self.pos.x + j >= 0 and self.pos.y + i <= 7 and self.pos.y + i >= 0:
          if squares[self.pos.y + i][self.pos.x + j].side != self.side:
            legalMoves.append(Pos(self.pos.x + j, self.pos.y + i))
    
    return legalMoves
class Knight(Piece):
  def __init__(self, pos, side):
    Piece.__init__(self, pos, "knight", side)
  
  def moves(self, hBoard):
    # Return an array of valid moves for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    if self.pos.x < 6 and self.pos.y < 7:
      if squares[self.pos.y + 1][self.pos.x + 2].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + 2, self.pos.y + 1)):
          legalMoves.append(Pos(self.pos.x + 2, self.pos.y + 1))
    if self.pos.x < 6 and self.pos.y > 0:
      if squares[self.pos.y - 1][self.pos.x + 2].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + 2, self.pos.y - 1)):
          legalMoves.append(Pos(self.pos.x + 2, self.pos.y - 1))
    if self.pos.x > 1 and self.pos.y < 7:
      if squares[self.pos.y + 1][self.pos.x - 2].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - 2, self.pos.y + 1)):
          legalMoves.append(Pos(self.pos.x - 2, self.pos.y + 1))
    if self.pos.x > 1 and self.pos.y > 0:
      if squares[self.pos.y - 1][self.pos.x - 2].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - 2, self.pos.y - 1)):
          legalMoves.append(Pos(self.pos.x - 2, self.pos.y - 1))
    if self.pos.x < 7 and self.pos.y < 6:
      if squares[self.pos.y + 2][self.pos.x + 1].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + 1, self.pos.y + 2)):
          legalMoves.append(Pos(self.pos.x + 1, self.pos.y + 2))
    if self.pos.x > 0 and self.pos.y < 6:
      if squares[self.pos.y + 2][self.pos.x - 1].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - 1, self.pos.y + 2)):
          legalMoves.append(Pos(self.pos.x - 1, self.pos.y + 2))
    if self.pos.x < 7 and self.pos.y > 1:
      if squares[self.pos.y - 2][self.pos.x + 1].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + 1, self.pos.y - 2)):
          legalMoves.append(Pos(self.pos.x + 1, self.pos.y - 2))
    if self.pos.x > 0 and self.pos.y > 1:
      if squares[self.pos.y - 2][self.pos.x - 1].side != self.side:
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - 1, self.pos.y - 2)):
          legalMoves.append(Pos(self.pos.x - 1, self.pos.y - 2))
    
    return legalMoves
  
  def attacks(self, hBoard):
    # Return an array of valid attacks for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    if self.pos.x < 6 and self.pos.y < 7:
      if squares[self.pos.y + 1][self.pos.x + 2].side != self.side:
        legalMoves.append(Pos(self.pos.x + 2, self.pos.y + 1))
    if self.pos.x < 6 and self.pos.y > 0:
      if squares[self.pos.y - 1][self.pos.x + 2].side != self.side:
        legalMoves.append(Pos(self.pos.x + 2, self.pos.y - 1))
    if self.pos.x > 1 and self.pos.y < 7:
      if squares[self.pos.y + 1][self.pos.x - 2].side != self.side:
        legalMoves.append(Pos(self.pos.x - 2, self.pos.y + 1))
    if self.pos.x > 1 and self.pos.y > 0:
      if squares[self.pos.y - 1][self.pos.x - 2].side != self.side:
        legalMoves.append(Pos(self.pos.x - 2, self.pos.y - 1))
    if self.pos.x < 7 and self.pos.y < 6:
      if squares[self.pos.y + 2][self.pos.x + 1].side != self.side:
        legalMoves.append(Pos(self.pos.x + 1, self.pos.y + 2))
    if self.pos.x > 0 and self.pos.y < 6:
      if squares[self.pos.y + 2][self.pos.x - 1].side != self.side:
        legalMoves.append(Pos(self.pos.x - 1, self.pos.y + 2))
    if self.pos.x < 7 and self.pos.y > 1:
      if squares[self.pos.y - 2][self.pos.x + 1].side != self.side:
        legalMoves.append(Pos(self.pos.x + 1, self.pos.y - 2))
    if self.pos.x > 0 and self.pos.y > 1:
      if squares[self.pos.y - 2][self.pos.x - 1].side != self.side:
        legalMoves.append(Pos(self.pos.x - 1, self.pos.y - 2))
    
    return legalMoves
class Rook(Piece):
  def __init__(self, pos, side):
    Piece.__init__(self, pos, "rook", side)
    self.canCastle = True
  
  def moves(self, hBoard):
    # Return an array of valid moves for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    # For the rook, legal moves are straight in any direction until it hits a piece.
    # Go in a direction until a nonempty square is hit.
    # left
    if self.pos.x != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y][self.pos.x - i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - i, self.pos.y)):
          legalMoves.append(Pos(self.pos.x - i, self.pos.y))
        i += 1
        if self.pos.x - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y][self.pos.x - i].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - i, self.pos.y)):
            legalMoves.append(Pos(self.pos.x - i, self.pos.y))
    # right
    if self.pos.x != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y][self.pos.x + i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + i, self.pos.y)):
          legalMoves.append(Pos(self.pos.x + i, self.pos.y))
        i += 1
        if self.pos.x + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y][self.pos.x + i].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + i, self.pos.y)):
            legalMoves.append(Pos(self.pos.x + i, self.pos.y))
    # up
    if self.pos.y != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y - i][self.pos.x].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y - i)):
          legalMoves.append(Pos(self.pos.x, self.pos.y - i))
        i += 1
        if self.pos.y - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y - i][self.pos.x].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y - i)):
            legalMoves.append(Pos(self.pos.x, self.pos.y - i))
    # down
    if self.pos.y != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y + i][self.pos.x].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y + i)):
          legalMoves.append(Pos(self.pos.x, self.pos.y + i))
        i += 1
        if self.pos.y + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y + i][self.pos.x].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x, self.pos.y + i)):
            legalMoves.append(Pos(self.pos.x, self.pos.y + i))
    
    return legalMoves
  
  def attacks(self, hBoard):
    # Return an array of valid attacks for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    # For the rook, legal moves are straight in any direction until it hits a piece.
    # Go in a direction until a nonempty square is hit.
    # left
    if self.pos.x != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y][self.pos.x - i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x - i, self.pos.y))
        i += 1
        if self.pos.x - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y][self.pos.x - i].side != self.side:
          legalMoves.append(Pos(self.pos.x - i, self.pos.y))
    # right
    if self.pos.x != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y][self.pos.x + i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x + i, self.pos.y))
        i += 1
        if self.pos.x + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y][self.pos.x + i].side != self.side:
          legalMoves.append(Pos(self.pos.x + i, self.pos.y))
    # up
    if self.pos.y != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y - i][self.pos.x].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x, self.pos.y - i))
        i += 1
        if self.pos.y - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y - i][self.pos.x].side != self.side:
          legalMoves.append(Pos(self.pos.x, self.pos.y - i))
    # down
    if self.pos.y != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y + i][self.pos.x].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x, self.pos.y + i))
        i += 1
        if self.pos.y + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y + i][self.pos.x].side != self.side:
          legalMoves.append(Pos(self.pos.x, self.pos.y + i))
    
    return legalMoves
class Bishop(Piece):
  def __init__(self, pos, side):
    Piece.__init__(self, pos, "bishop", side)
  
  def moves(self, hBoard):
    # Return an array of valid moves for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    # For the bishop, legal moves are diagonal in any direction until it hits a piece.
    # Go in a direction until a nonempty square is hit.
    # up-left
    if self.pos.x != 0 and self.pos.y != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y - i][self.pos.x - i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - i, self.pos.y - i)):
          legalMoves.append(Pos(self.pos.x - i, self.pos.y - i))
        i += 1
        if self.pos.x - i < 0 or self.pos.y - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y - i][self.pos.x - i].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - i, self.pos.y - i)):
            legalMoves.append(Pos(self.pos.x - i, self.pos.y - i))
    # up-right
    if self.pos.x != 7 and self.pos.y != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y - i][self.pos.x + i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + i, self.pos.y - i)):
          legalMoves.append(Pos(self.pos.x + i, self.pos.y - i))
        i += 1
        if self.pos.x + i > 7 or self.pos.y - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y - i][self.pos.x + i].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + i, self.pos.y - i)):
            legalMoves.append(Pos(self.pos.x + i, self.pos.y - i))
    # down-left
    if self.pos.x != 0 and self.pos.y != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y + i][self.pos.x - i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - i, self.pos.y + i)):
          legalMoves.append(Pos(self.pos.x - i, self.pos.y + i))
        i += 1
        if self.pos.x - i < 0 or self.pos.y + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y + i][self.pos.x - i].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x - i, self.pos.y + i)):
            legalMoves.append(Pos(self.pos.x - i, self.pos.y + i))
    # down-right
    if self.pos.x != 7 and self.pos.y != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y + i][self.pos.x + i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + i, self.pos.y + i)):
          legalMoves.append(Pos(self.pos.x + i, self.pos.y + i))
        i += 1
        if self.pos.x + i > 7 or self.pos.y + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y + i][self.pos.x + i].side != self.side:
          if hBoard.keepsKingSafe(self.pos, Pos(self.pos.x + i, self.pos.y + i)):
            legalMoves.append(Pos(self.pos.x + i, self.pos.y + i))
    
    return legalMoves
  
  def attacks(self, hBoard):
    # Return an array of valid attacks for this piece.
    squares = hBoard.squares
    legalMoves = []
    
    # For the bishop, legal moves are diagonal in any direction until it hits a piece.
    # Go in a direction until a nonempty square is hit.
    # up-left
    if self.pos.x != 0 and self.pos.y != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y - i][self.pos.x - i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x - i, self.pos.y - i))
        i += 1
        if self.pos.x - i < 0 or self.pos.y - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y - i][self.pos.x - i].side != self.side:
          legalMoves.append(Pos(self.pos.x - i, self.pos.y - i))
    # up-right
    if self.pos.x != 7 and self.pos.y != 0:
      i = 1
      onEdge = False
      while squares[self.pos.y - i][self.pos.x + i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x + i, self.pos.y - i))
        i += 1
        if self.pos.x + i > 7 or self.pos.y - i < 0:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y - i][self.pos.x + i].side != self.side:
          legalMoves.append(Pos(self.pos.x + i, self.pos.y - i))
    # down-left
    if self.pos.x != 0 and self.pos.y != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y + i][self.pos.x - i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x - i, self.pos.y + i))
        i += 1
        if self.pos.x - i < 0 or self.pos.y + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y + i][self.pos.x - i].side != self.side:
          legalMoves.append(Pos(self.pos.x - i, self.pos.y + i))
    # down-right
    if self.pos.x != 7 and self.pos.y != 7:
      i = 1
      onEdge = False
      while squares[self.pos.y + i][self.pos.x + i].name == None:
        # Check to be sure that we aren't going to be checking outside of the hBoard.
        legalMoves.append(Pos(self.pos.x + i, self.pos.y + i))
        i += 1
        if self.pos.x + i > 7 or self.pos.y + i > 7:
          onEdge = True
          break
      if not onEdge:
        # Check we aren't taking a piece
        if squares[self.pos.y + i][self.pos.x + i].side != self.side:
          legalMoves.append(Pos(self.pos.x + i, self.pos.y + i))
    
    return legalMoves
class Queen(Piece):
  def __init__(self, pos, side):
    Piece.__init__(self, pos, "queen", side)
  
  def moves(self, hBoard):
    # Return an array of valid moves for this piece.
    legalMoves = []
    
    # For the queen, legal moves are the combination of legal bishop and rook moves.
    # Rook moves:
    rook = Rook(self.pos, self.side).moves(hBoard)
    # Bishop moves:
    bishop = Bishop(self.pos, self.side).moves(hBoard)
    
    for move in rook:
      legalMoves.append(move)
    for move in bishop:
      legalMoves.append(move)
    
    return legalMoves
  
  def attacks(self, hBoard):
    # Return an array of valid attacks for this piece.
    legalMoves = []
    
    # For the queen, legal moves are the combination of legal bishop and rook moves.
    # Rook moves:
    rook = Rook(self.pos, self.side).attacks(hBoard)
    # Bishop moves:
    bishop = Bishop(self.pos, self.side).attacks(hBoard)
    
    for move in rook:
      legalMoves.append(move)
    for move in bishop:
      legalMoves.append(move)
    
    return legalMoves

class UI:
  def __init__(self):
    self.takenPieces = {
      "white": [],
      "black": []
    }
    self.startTime = time.time()
    self.whiteTime = 0
    self.blackTime = 0
    
    self.state = "information"
  
  def update(self):
    if self.state == "information":
      fill(60, 60, 60)
      rect(0, SCREENSIZE, SCREENSIZE, UIHEIGHT)
      
      self.turnDisplay()
      self.updateTime()
      self.timeDisplay()
      self.capturedDisplay()
    if self.state == "promotion":
      self.promotionChoicesDisplay()
  
  def turnDisplay(self):
    fill(255)
    textAlign(CENTER, CENTER)
    textSize(UIHEIGHT // 3)
    text("It's " + turn + "'s turn.", HALFSCREENSIZE, SCREENSIZE + UIHEIGHT / 4)
  
  def updateTime(self):
    if turn == "white":
      self.whiteTime = time.time() - self.startTime - self.blackTime
    else:
      self.blackTime = time.time() - self.startTime - self.whiteTime
  
  def timeDisplay(self):
    fill(255)
    textSize(UIHEIGHT // 6)
    textAlign(LEFT, BOTTOM)
    text("White's time: %0.2f" %(self.whiteTime), HALFSCREENSIZE + 6 * SCREENSIZE // 25, SCREENSIZE + 25 * UIHEIGHT // 36)
    text("Black's time: %0.2f" %(self.blackTime), HALFSCREENSIZE + 6 * SCREENSIZE // 25, SCREENSIZE + 33 * UIHEIGHT // 36)
  
  def capturedDisplay(self):
    fill(255)
    textAlign(CENTER, CENTER)
    textSize(UIHEIGHT // 6)
    text("White has captured:", HALFSCREENSIZE - 3 * SCREENSIZE // 8, SCREENSIZE + 4 * UIHEIGHT // 7)
    text("Black has captured:", HALFSCREENSIZE - 3 * SCREENSIZE // 8, SCREENSIZE + 4 * UIHEIGHT // 5)
    
    # White
    whitesTaken = ""
    for piece in self.takenPieces["white"]:
      whitesTaken += piece
    # Black
    blacksTaken = ""
    for piece in self.takenPieces["black"]:
      blacksTaken += piece
    
    textAlign(LEFT, BOTTOM)
    textSize(3 * UIHEIGHT // 14)
    fill(0)
    text(whitesTaken, HALFSCREENSIZE - SCREENSIZE // 4, SCREENSIZE + 25 * UIHEIGHT // 36)
    fill(220)
    text(blacksTaken, HALFSCREENSIZE - SCREENSIZE // 4, SCREENSIZE + 33 * UIHEIGHT // 36)
  
  def promotionChoicesDisplay(self):
    fill(140)
    rect(0, SCREENSIZE, SCREENSIZE, UIHEIGHT)
    fill(220)
    textAlign(CENTER, CENTER)
    textSize(UIHEIGHT)
    text("♞", HALFSCREENSIZE - HALFSCREENSIZE // 2, SCREENSIZE + UIHEIGHT // 2)
    text("♛", HALFSCREENSIZE + HALFSCREENSIZE // 2, SCREENSIZE + UIHEIGHT // 2)
    textSize(UIHEIGHT // 2)
    text("or", HALFSCREENSIZE, SCREENSIZE + UIHEIGHT // 2)
    
    # Shade moused over regions.
    if mouseY > SCREENSIZE:
      if mouseX < 2 * SCREENSIZE // 5:
        fill(255, 255, 255, 50)
        rect(0, SCREENSIZE, 2 * SCREENSIZE // 5, UIHEIGHT)
      if mouseX > 3 * SCREENSIZE // 5:
        fill(255, 255, 255, 50)
        rect(3 * SCREENSIZE // 5, SCREENSIZE, 2 * SCREENSIZE // 5, UIHEIGHT)
  
  def promotionChoice(self, x, y):
    if x < 2 * SCREENSIZE // 5:
      # Knight
      return "knight"
    elif x > 3 * SCREENSIZE // 5:
      # Queen
      return "queen"
    else:
      return None

board = Board()
ui = UI()

def initializeBoard():
  # Pawns:
  for i in xrange(8):
    board.squares[1][i] = Pawn(Pos(i, 1), "white")
    board.squares[6][i] = Pawn(Pos(i, 6), "black")
  # Rooks:
  board.squares[0][0] = Rook(Pos(0, 0), "white")
  board.squares[0][7] = Rook(Pos(7, 0), "white")
  board.squares[7][0] = Rook(Pos(0, 7), "black")
  board.squares[7][7] = Rook(Pos(7, 7), "black")
  # Knights:
  board.squares[0][1] = Knight(Pos(1, 0), "white")
  board.squares[0][6] = Knight(Pos(6, 0), "white")
  board.squares[7][1] = Knight(Pos(1, 7), "black")
  board.squares[7][6] = Knight(Pos(6, 7), "black")
  # Bishops:
  board.squares[0][2] = Bishop(Pos(2, 0), "white")
  board.squares[0][5] = Bishop(Pos(5, 0), "white")
  board.squares[7][2] = Bishop(Pos(2, 7), "black")
  board.squares[7][5] = Bishop(Pos(5, 7), "black")
  # Kings:
  board.squares[0][3] = King(Pos(3, 0), "white")
  board.squares[7][3] = King(Pos(3, 7), "black")
  # Queens:
  board.squares[0][4] = Queen(Pos(4, 0), "white")
  board.squares[7][4] = Queen(Pos(4, 7), "black")

def mousePressed():
  board.click(mouseX, mouseY)
  # Only necessary to update whenever the mouse is clicked.
  update()

def update():
  board.displayBoard()
  board.updatePieces()

initializeBoard()

def setup():
  size(SCREENSIZE, SCREENSIZE + UIHEIGHT)
  frameRate(FRAMERATE)
  noStroke()
  update()

def draw():
  ui.update()

# Run once to initialize the display, then only update whenever a click occurs.

run()
