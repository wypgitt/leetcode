#
# @lc app=leetcode id=1000 lang=python3
#
# [1000] Minimum Cost to Merge Stones
#
# https://leetcode.com/problems/minimum-cost-to-merge-stones/description/
#
# algorithms
# Hard (46.61%)
# Likes:    2663
# Dislikes: 116
# Total Accepted:    54.6K
# Total Submissions: 117K
# Testcase Example:  "[3,2,4,1]"
#
# There are n piles of stones arranged in a row. The i^th pile has stones[i]
# stones.
#
# A move consists of merging exactly k consecutive piles into one pile, and the
# cost of this move is equal to the total number of stones in these k piles.
#
# Return the minimum cost to merge all piles of stones into one pile. If it is
# impossible, return -1.
#
# Example 1:
#
# Input: stones = [3,2,4,1], k = 2
# Output: 20
# Explanation: We start with [3, 2, 4, 1].
# We merge [3, 2] for a cost of 5, and we are left with [5, 4, 1].
# We merge [4, 1] for a cost of 5, and we are left with [5, 5].
# We merge [5, 5] for a cost of 10, and we are left with [10].
# The total cost was 20, and this is the minimum possible.
#
# Example 2:
#
# Input: stones = [3,2,4,1], k = 3
# Output: -1
# Explanation: After any merge operation, there are 2 piles left, and we can't
# merge anymore. So the task is impossible.
#
# Example 3:
#
# Input: stones = [3,5,1,2,6], k = 3
# Output: 25
# Explanation: We start with [3, 5, 1, 2, 6].
# We merge [5, 1, 2] for a cost of 8, and we are left with [3, 8, 6].
# We merge [3, 8, 6] for a cost of 17, and we are left with [17].
# The total cost was 25, and this is the minimum possible.
#
# Constraints:
#
# n == stones.length
#
# 1 <= n <= 30
#
# 1 <= stones[i] <= 100
#
# 2 <= k <= 30
#

# @lc code=start
from typing import List


class Solution:
    def mergeStones(self, stones: List[int], k: int) -> int:
        """
        Interview explanation:
        Merging n piles into 1 by repeatedly merging k consecutive piles is
        possible iff (n-1) % (k-1) == 0. Interval DP: dp[i][j] = min cost to
        merge stones[i..j] into as few piles as allowed (ultimately the cost
        to merge into 1 pile when length permits). Cost of the final merge of
        an interval into 1 pile is sum(stones[i..j]) plus costs of submerges.

        Algorithm (interval DP):
        - If (n-1)%(k-1)!=0 return -1.
        - prefix sums for range sums.
        - dp[i][j] = min over m=i..j-1 step (k-1): dp[i][m]+dp[m+1][j].
        - If (j-i)%(k-1)==0: dp[i][j] += sum(i..j) (final merge into one).

        Complexity: O(n^3 / (k-1)) ~ O(n^3) time, O(n^2) space.
        """
        n = len(stones)
        if (n - 1) % (k - 1) != 0:
            return -1
        prefix = [0] * (n + 1)
        for i, x in enumerate(stones):
            prefix[i + 1] = prefix[i] + x

        INF = 10**18
        dp = [[0] * n for _ in range(n)]
        for length in range(k, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                best = INF
                for m in range(i, j, k - 1):
                    best = min(best, dp[i][m] + dp[m + 1][j])
                if (j - i) % (k - 1) == 0:
                    best += prefix[j + 1] - prefix[i]
                dp[i][j] = best
        return dp[0][n - 1]
# @lc code=end
