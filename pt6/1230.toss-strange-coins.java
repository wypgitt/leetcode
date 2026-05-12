class Solution {
    public double probabilityOfHeads(double[] prob, int target) {
        double[] dp = new double[target + 1];
        dp[0] = 1.0;

        for (double p : prob) {
            for (int heads = target; heads >= 1; heads--) {
                dp[heads] = dp[heads] * (1 - p) + dp[heads - 1] * p;
            }
            dp[0] *= 1 - p;
        }

        return dp[target];
    }
}

/*
Explanation

dp[h] is the probability of exactly h heads after processing some prefix of
coins. For a coin with head probability p, h heads can come from old h heads
and a tail, or old h - 1 heads and a head.

The DP array is updated from target down to 1 so dp[h - 1] still represents the
previous coin layer. This is the standard one-dimensional dynamic programming
compression.

Edge cases: target == 0 only multiplies tail probabilities; probabilities 0 or
1 work naturally; impossible head counts remain 0.

Time complexity: O(n * target).
Space complexity: O(target).
*/
