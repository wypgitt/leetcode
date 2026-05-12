import java.util.Arrays;

class Solution {
    public int maxSumDivThree(int[] nums) {
        int negative = Integer.MIN_VALUE / 4;
        int[] dp = {0, negative, negative};

        for (int num : nums) {
            int[] prev = Arrays.copyOf(dp, 3);
            for (int r = 0; r < 3; r++) {
                int next = (r + num) % 3;
                dp[next] = Math.max(dp[next], prev[r] + num);
            }
        }

        return dp[0];
    }
}

/*
Explanation

dp[r] stores the largest sum seen so far with remainder r modulo 3. For each
number, either skip it or add it to a previous remainder class. Adding num
moves remainder r to (r + num) % 3.

Only three DP states are needed because divisibility by 3 depends only on the
remainder. Copying the previous array prevents using the same number twice in
one iteration.

Edge cases: impossible remainders start very negative; answer can be 0; numbers
already divisible by 3 accumulate in dp[0].

Time complexity: O(n).
Space complexity: O(1).
*/
