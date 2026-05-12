import java.util.*;

class Solution {
    public String alphabetBoardPath(String target) {
        int row = 0;
        int col = 0;
        StringBuilder moves = new StringBuilder();

        for (char ch : target.toCharArray()) {
            int index = ch - 'a';
            int nextRow = index / 5;
            int nextCol = index % 5;

            while (row > nextRow) {
                moves.append('U');
                row--;
            }
            while (col > nextCol) {
                moves.append('L');
                col--;
            }
            while (col < nextCol) {
                moves.append('R');
                col++;
            }
            while (row < nextRow) {
                moves.append('D');
                row++;
            }
            moves.append('!');
        }

        return moves.toString();
    }
}

