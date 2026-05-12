import java.util.*;

class Solution {
    public int numRollsToTarget(int n, int k, int target) {
        int mod = 1_000_000_007;
        int[] dp = new int[target + 1];
        dp[0] = 1;

        for (int dice = 0; dice < n; dice++) {
            int[] next = new int[target + 1];
            for (int total = 1; total <= target; total++) {
                long ways = 0;
                for (int face = 1; face <= Math.min(k, total); face++) {
                    ways += dp[total - face];
                }
                next[total] = (int) (ways % mod);
            }
            dp = next;
        }

        return dp[target];
    }
}

