#
# @lc app=leetcode id=3825 lang=python3
#
# [3825] Longest Strictly Increasing Subsequence With Non-Zero Bitwise AND
#
# https://leetcode.com/problems/longest-strictly-increasing-subsequence-with-non-zero-bitwise-and/description/
#
# algorithms
# Medium (50.58%)
# Likes:    114
# Dislikes: 2
# Total Accepted:    23.3K
# Total Submissions: 46K
# Testcase Example:  "[5,4,7]"
#
#
# You are given an integer array nums.
#
# Return the length of the longest strictly increasing subsequence in nums
# whose bitwise AND is non-zero. If no such subsequence exists, return 0.
#
# Example 1:
#
# Input: nums = [5,4,7]
#
# Output: 2
#
# Explanation:
#
# One longest strictly increasing subsequence is [5, 7]. The bitwise AND
# is 5 AND 7 = 5, which is non-zero.
#
# Example 2:
#
# Input: nums = [2,3,6]
#
# Output: 3
#
# Explanation:
#
# The longest strictly increasing subsequence is [2, 3, 6]. The bitwise
# AND is 2 AND 3 AND 6 = 2, which is non-zero.
#
# Example 3:
#
# Input: nums = [0,1]
#
# Output: 1
#
# Explanation:
#
# One longest strictly increasing subsequence is [1]. The bitwise AND is
# 1, which is non-zero.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9​​​​​​​
#

# @lc code=start

from bisect import bisect_left
from typing import List


class Solution:
    def longestSubsequence(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Non-zero AND means some bit is set in every chosen value. For each
        bit, take LIS over numbers with that bit; answer is the max LIS.

        Algorithm:
        - For bit i in 0..bit_length(max)-1, collect nums with that bit set.
        - Patience-sorting LIS via bisect_left; take maximum length.

        Complexity: O(32 * n log n) time, O(n) space.
        """
        def lis(arr: List[int]) -> int:
            g: List[int] = []
            for x in arr:
                j = bisect_left(g, x)
                if j == len(g):
                    g.append(x)
                else:
                    g[j] = x
            return len(g)

        ans = 0
        m = max(nums).bit_length()
        for i in range(m):
            arr = [x for x in nums if (x >> i) & 1]
            ans = max(ans, lis(arr))
        return ans
# @lc code=end
