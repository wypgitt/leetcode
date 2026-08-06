/*
 * @lc app=leetcode id=656 lang=java
 *
 * [656] Coin Path
 *
 * DP from right to left: dp[i] is minimum cost from i to the end and next[i]
 * stores the chosen next index. Candidates are scanned in increasing order, so
 * equal costs keep the lexicographically smallest next step.
 *
 * Time: O(n * maxJump). Space: O(n).
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

// @lc code=start
class Solution {
    public List<Integer> cheapestJump(int[] coins, int maxJump) {
        int n = coins.length;
        long inf = Long.MAX_VALUE / 4;
        long[] dp = new long[n];
        int[] next = new int[n];
        Arrays.fill(dp, inf);
        Arrays.fill(next, -1);

        if (coins[n - 1] != -1) {
            dp[n - 1] = coins[n - 1];
        }

        for (int i = n - 2; i >= 0; i--) {
            if (coins[i] == -1) {
                continue;
            }
            int furthest = Math.min(n - 1, i + maxJump);
            for (int candidate = i + 1; candidate <= furthest; candidate++) {
                if (dp[candidate] == inf) {
                    continue;
                }
                long total = coins[i] + dp[candidate];
                if (total < dp[i]) {
                    dp[i] = total;
                    next[i] = candidate;
                }
            }
        }

        List<Integer> path = new ArrayList<>();
        if (dp[0] == inf) {
            return path;
        }

        int index = 0;
        while (index != -1) {
            path.add(index + 1);
            if (index == n - 1) {
                break;
            }
            index = next[index];
        }
        return path;
    }
}
// @lc code=end
