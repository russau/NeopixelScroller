import time
from random import randint


class Scroller(object):

    def __init__(self, emitter):
        self.emitter = emitter

    def scrollText(self):
        width = 6 * 10
        height = 8
        board = []
        for y in range(height):
            row = []
            for x in range(width):
                color = {'r':0xe4, 'g':0xde, 'b':0x00} if (randint(0, 9) % 2) else {'r':0x00, 'g':0x4e, 'b':0xe4}
                row.append(color)
            board.append(row)


        for _ in range(width):
            for y in range(height):
                board[y].pop(0)

            squares = boardToLights(board)
            self.emitter(squares)
            time.sleep(0.05)


def boardToLights(board):
    array_pos = -1
    width = len(board[0])
    height = len(board)
    squares = [{'r':0, 'g':0, 'b':0}] * 8 * 16

    for y in range(min(height, 8)):
        for x in range(min(width, 16)):
            if x < 8:
                array_pos = (7-y) * 8 + x
                squares[array_pos] = board[y][x]
            elif x < 16:
                array_pos = (7-y) * 8 + x-8 + 64
                squares[array_pos] = board[y][x]

    return squares

def printBoard(board):
    width = len(board[0])
    for y in range(len(board)-1, -1, -1):
        for x in range(len(board[y])):
            print board[y][x],
        print ""
    print " ".join("=" for _ in range(width))
