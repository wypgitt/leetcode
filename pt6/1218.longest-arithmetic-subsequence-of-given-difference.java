import java.util.HashMap;
import java.util.Map;

class Solution {
    public int longestSubsequence(int[] arr, int difference) {
        Map<Integer, Integer> bestEndingAt = new HashMap<>();
        int best = 0;

        for (int num : arr) {
            int length = bestEndingAt.getOrDefault(num - difference, 0) + 1;
            bestEndingAt.put(num, length);
            best = Math.max(best, length);
        }

        return best;
    }
}

/*
Explanation

Let dp[x] be the longest valid subsequence ending with value x after scanning
the processed prefix. For a new number num, the previous value must be
num - difference, so dp[num] = dp[num - difference] + 1.

HashMap is the right Java data structure because values may be negative or
large, making array indexing inappropriate. Scanning left to right preserves
subsequence order.

Edge cases: difference == 0 counts repeated values; negative differences work
with the same formula; missing predecessors default to length 0.

Time complexity: O(n) average.
Space complexity: O(u), where u is the number of distinct values.
*/
