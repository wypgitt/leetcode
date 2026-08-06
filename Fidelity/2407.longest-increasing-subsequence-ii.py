#
# @lc app=leetcode id=2407 lang=python3
#
# [2407] Longest Increasing Subsequence II
#
# https://leetcode.com/problems/longest-increasing-subsequence-ii/description/
#
# algorithms
# Hard (26.44%)
# Likes:    974
# Dislikes: 41
# Total Accepted:    25.8K
# Total Submissions: 97.6K
# Testcase Example:  "[4,2,1,4,3,4,5,8,15]\n3"
#
# You are given an integer array nums and an integer k.
#
# Find the longest subsequence of nums that meets the following requirements:
#
#
# The subsequence is strictly increasing and
#
#
# The difference between adjacent elements in the subsequence is at most k.
#
# Return the length of the longest subsequence that meets the requirements.
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
#
#
# Example 1:
#
# Input: nums = [4,2,1,4,3,4,5,8,15], k = 3
# Output: 5
# Explanation:
# The longest subsequence that meets the requirements is [1,3,4,5,8].
# The subsequence has a length of 5, so we return 5.
# Note that the subsequence [1,3,4,5,8,15] does not meet the requirements
# because 15 - 8 = 7 is larger than 3.
#
# Example 2:
#
# Input: nums = [7,4,5,1,8,12,4,7], k = 5
# Output: 4
# Explanation:
# The longest subsequence that meets the requirements is [4,5,8,12].
# The subsequence has a length of 4, so we return 4.
#
# Example 3:
#
# Input: nums = [1,5], k = 1
# Output: 1
# Explanation:
# The longest subsequence that meets the requirements is [1].
# The subsequence has a length of 1, so we return 1.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i], k <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def lengthOfLIS(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Longest increasing subsequence where consecutive values differ by at most k.

        Algorithm:
        - Segment tree over value domain: for x, query max dp in [x-k, x-1], set
          dp[x] = that + 1; track global max.

        Complexity: O(n log M) time, O(M) space (M = max(nums)).
        """
        m = max(nums)
        size = 1
        while size <= m:
            size <<= 1
        tree = [0] * (2 * size)

        def query(l: int, r: int) -> int:
            if l > r:
                return 0
            l += size
            r += size
            res = 0
            while l <= r:
                if l & 1:
                    res = max(res, tree[l])
                    l += 1
                if not r & 1:
                    res = max(res, tree[r])
                    r -= 1
                l >>= 1
                r >>= 1
            return res

        def update(i: int, val: int) -> None:
            i += size
            tree[i] = max(tree[i], val)
            i >>= 1
            while i:
                tree[i] = max(tree[i << 1], tree[i << 1 | 1])
                i >>= 1

        ans = 0
        for x in nums:
            best = query(max(1, x - k), x - 1) + 1
            update(x, best)
            ans = max(ans, best)
        return ans
# @lc code=end
