import java.util.*;

/**
 * Algorithm:
 * Simulate the row movement of the zigzag. Append each character to its row,
 * switching direction at the top and bottom rows, then concatenate rows.
 *
 * Java data structures:
 * StringBuilder[] stores row buffers; appending is amortized O(1).
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public String convert(String s, int numRows) {
        if (numRows == 1 || numRows >= s.length()) {
            return s;
        }
        StringBuilder[] rows = new StringBuilder[numRows];
        for (int i = 0; i < numRows; i++) {
            rows[i] = new StringBuilder();
        }
        int row = 0;
        int step = 1;
        for (int i = 0; i < s.length(); i++) {
            rows[row].append(s.charAt(i));
            if (row == 0) {
                step = 1;
            } else if (row == numRows - 1) {
                step = -1;
            }
            row += step;
        }
        StringBuilder ans = new StringBuilder();
        for (StringBuilder builder : rows) {
            ans.append(builder);
        }
        return ans.toString();
    }
}

