import java.util.*;

/**
 * Algorithm:
 * Bottom-up DP: the best path from a cell is its value plus the cheaper of the
 * two adjacent best paths below it. Initialize dp with the last row and update
 * upward in place.
 *
 * Java data structures:
 * int[] dp stores one row of dynamic programming values.
 *
 * Complexity:
 * Time O(total cells), space O(number of rows).
 */
class Solution {
    public int minimumTotal(List<List<Integer>> triangle) {
        int n = triangle.size();
        int[] dp = new int[n];
        for (int i = 0; i < n; i++) {
            dp[i] = triangle.get(n - 1).get(i);
        }
        for (int r = n - 2; r >= 0; r--) {
            for (int c = 0; c < triangle.get(r).size(); c++) {
                dp[c] = triangle.get(r).get(c) + Math.min(dp[c], dp[c + 1]);
            }
        }
        return dp[0];
    }
}

