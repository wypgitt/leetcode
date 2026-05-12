from __future__ import annotations


class Solution:
    def alphabetBoardPath(self, target: str) -> str:
        row = col = 0
        moves = []

        for char in target:
            index = ord(char) - ord("a")
            next_row, next_col = divmod(index, 5)

            while row > next_row:
                moves.append("U")
                row -= 1
            while col > next_col:
                moves.append("L")
                col -= 1
            while col < next_col:
                moves.append("R")
                col += 1
            while row < next_row:
                moves.append("D")
                row += 1

            moves.append("!")

        return "".join(moves)

