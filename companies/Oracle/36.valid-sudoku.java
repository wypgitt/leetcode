import java.util.*;

/**
 * Algorithm:
 * Check each filled digit against the row, column, and 3x3 box sets that have
 * already seen digits. A repeated digit in any unit makes the board invalid.
 *
 * Java data structures:
 * HashSet<Character>[] stores seen digits for nine rows, columns, and boxes.
 *
 * Complexity:
 * O(81) time and O(81) space, both constant for a 9x9 board.
 */
class Solution {
    public boolean isValidSudoku(char[][] board) {
        Set<Character>[] rows = new HashSet[9];
        Set<Character>[] cols = new HashSet[9];
        Set<Character>[] boxes = new HashSet[9];
        for (int i = 0; i < 9; i++) {
            rows[i] = new HashSet<>();
            cols[i] = new HashSet<>();
            boxes[i] = new HashSet<>();
        }

        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                char val = board[r][c];
                if (val == '.') {
                    continue;
                }
                int b = (r / 3) * 3 + c / 3;
                if (rows[r].contains(val) || cols[c].contains(val) || boxes[b].contains(val)) {
                    return false;
                }
                rows[r].add(val);
                cols[c].add(val);
                boxes[b].add(val);
            }
        }
        return true;
    }
}

