import java.util.HashMap;
import java.util.Map;

/*
 * 1027. Longest Arithmetic Subsequence
 */
class Solution {
    public int longestArithSeqLength(int[] nums) {
        @SuppressWarnings("unchecked")
        Map<Integer, Integer>[] dp = new HashMap[nums.length];
        for (int i = 0; i < nums.length; i++) {
            dp[i] = new HashMap<>();
        }

        int best = 2;
        for (int right = 0; right < nums.length; right++) {
            for (int left = 0; left < right; left++) {
                int diff = nums[right] - nums[left];
                int length = dp[left].getOrDefault(diff, 1) + 1;
                dp[right].put(diff, Math.max(dp[right].getOrDefault(diff, 1), length));
                best = Math.max(best, dp[right].get(diff));
            }
        }

        return best;
    }
}

/*
Interview Explanation

Core idea:
An arithmetic subsequence is defined by its last index and common difference.
If a sequence ending at left has difference d, nums[right] can extend it when
nums[right] - nums[left] == d.

Java data structures:
- Map<Integer, Integer>[] dp stores, for every index, the best length for each
  difference ending at that index.
- HashMap is appropriate because differences can be negative and sparse.

Algorithm:
For every pair left < right:
1. Compute diff = nums[right] - nums[left].
2. Extend dp[left][diff] by one, defaulting to length 1 before adding nums[right].
3. Store the best length in dp[right][diff].
4. Track the global maximum.

Correctness:
Every arithmetic subsequence of length at least two has a final pair
(left, right) and a common difference diff. The transition extends the optimal
subsequence ending at left with that diff. Since all possible final pairs are
processed, the best recorded length is the longest arithmetic subsequence.

Complexity:
There are O(n^2) pairs and HashMap operations are O(1) average, so time is
O(n^2). In the worst case, each pair creates a distinct difference, so space is
O(n^2).

Edge cases:
- All values equal use diff 0.
- Decreasing sequences use negative differences.
- Minimum length 2 returns 2.
*/
