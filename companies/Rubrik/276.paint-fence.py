#
# @lc app=leetcode id=276 lang=python3
#
# [276] Paint Fence
#
# https://leetcode.com/problems/paint-fence/description/
#
# algorithms
# Medium (48.50%)
# Likes:    1642
# Dislikes: 398
# Total Accepted:    131.2K
# Total Submissions: 270.5K
# Testcase Example:  "3\n2"
#
#
# You are painting a fence of n posts with k different colors. You must
# paint the posts following these rules:
#
# Every post must be painted exactly one color.
#
# There cannot be three or more consecutive posts with the same color.
#
# Given the two integers n and k, return the number of ways you can paint
# the fence.
#
# Example 1:
#
# Input: n = 3, k = 2
# Output: 6
# Explanation: All the possibilities are shown.
# Note that painting all the posts red or all the posts green is invalid
# because there cannot be three posts in a row with the same color.
#
# Example 2:
#
# Input: n = 1, k = 1
# Output: 1
#
# Example 3:
#
# Input: n = 7, k = 2
# Output: 42
#
# Constraints:
#
# 1 <= n <= 50
#
# 1 <= k <= 10^5
#
# The testcases are generated such that the answer is in the range [0,
# 2^31 - 1] for the given n and k.
#
# @lc code=start
class Solution:
    def numWays(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Paint n posts with k colors so no more than two adjacent posts share a
        color. Track ways ending with same-color pair vs different-color.

        Algorithm (DP):
        - same = ways where last two posts same color
        - diff = ways where last two posts different
        - Total for i posts: same + diff
        - Transition: same' = diff (paint same as previous); diff' = (same+diff)*(k-1)

        Complexity: O(n) time, O(1) space.
        """
        if n == 0:
            return 0
        if n == 1:
            return k
        same = k  # ways for 2 posts with same color: k choices (aa, bb, ...)
        # actually for 2 posts: same = k, diff = k*(k-1)
        same, diff = k, k * (k - 1)
        for _ in range(3, n + 1):
            same, diff = diff, (same + diff) * (k - 1)
        return same + diff
# @lc code=end

