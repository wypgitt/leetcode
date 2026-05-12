/*
 * 1035. Uncrossed Lines
 */
class Solution {
    public int maxUncrossedLines(int[] nums1, int[] nums2) {
        int[] dp = new int[nums2.length + 1];

        for (int value1 : nums1) {
            int previousDiagonal = 0;
            for (int j = 1; j <= nums2.length; j++) {
                int oldDpJ = dp[j];
                if (value1 == nums2[j - 1]) {
                    dp[j] = previousDiagonal + 1;
                } else {
                    dp[j] = Math.max(dp[j], dp[j - 1]);
                }
                previousDiagonal = oldDpJ;
            }
        }

        return dp[nums2.length];
    }
}

/*
Interview Explanation

Core idea:
Uncrossed lines are the Longest Common Subsequence problem. If we connect
nums1[i] to nums2[j], every later connection must use larger indices in both
arrays, exactly the LCS order constraint.

Java data structures:
- int[] dp compresses the usual 2D LCS table into one row.
- previousDiagonal stores the old dp[j - 1] from the previous row, which is
  needed when two values match.

Algorithm:
1. Iterate values of nums1 as rows.
2. Iterate nums2 left to right.
3. If values match, extend the previous diagonal by one.
4. Otherwise, take the best result from skipping one value from either array.

Correctness:
For every pair of prefixes, the optimal solution either matches the last
values if they are equal, or skips one of them if they are not. The update is
the LCS recurrence. Since every valid non-crossing line set is a common
subsequence and vice versa, the LCS length is the maximum number of lines.

Complexity:
Time is O(m * n). Space is O(n), where n is nums2.length.

Edge cases:
- No common numbers returns 0.
- Duplicates are handled by LCS ordering.
- One-element arrays work naturally.
*/
