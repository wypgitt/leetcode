#
# @lc app=leetcode id=3788 lang=python3
#
# [3788] Maximum Score of a Split
#
# https://leetcode.com/problems/maximum-score-of-a-split/description/
#
# algorithms
# Medium (51.70%)
# Likes:    71
# Dislikes: 7
# Total Accepted:    39.8K
# Total Submissions: 77.1K
# Testcase Example:  "[10,-1,3,-4,-5]"
#
#
# You are given an integer array nums of length n.
#
# Choose an index i such that 0 <= i < n - 1.
#
# For a chosen split index i:
#
# Let prefixSum(i) be the sum of nums[0] + nums[1] + ... + nums[i].
#
# Let suffixMin(i) be the minimum value among nums[i + 1], nums[i + 2],
# ..., nums[n - 1].
#
# The score of a split at index i is defined as:
#
# score(i) = prefixSum(i) - suffixMin(i)
#
# Return an integer denoting the maximum score over all valid split
# indices.
#
# Example 1:
#
# Input: nums = [10,-1,3,-4,-5]
#
# Output: 17
#
# Explanation:
#
# The optimal split is at i = 2, score(2) = prefixSum(2) - suffixMin(2) =
# (10 + (-1) + 3) - (-5) = 17.
#
# Example 2:
#
# Input: nums = [-7,-5,3]
#
# Output: -2
#
# Explanation:
#
# The optimal split is at i = 0, score(0) = prefixSum(0) - suffixMin(0) =
# (-7) - (-5) = -2.
#
# Example 3:
#
# Input: nums = [1,1]
#
# Output: 0
#
# Explanation:
#
# The only valid split is at i = 0, score(0) = prefixSum(0) - suffixMin(0)
# = 1 - 1 = 0.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# -10^9​​​​​​​ <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Score(i) = prefixSum(i) - min(nums[i+1:]). Precompute suffix minima, then
        scan left-to-right with a running prefix sum and take the max score.

        Algorithm:
        - suf[i] = min(nums[i:]); build from the right.
        - For i in [0, n-2]: pre += nums[i]; ans = max(ans, pre - suf[i+1]).

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        suf = [0] * n
        suf[-1] = nums[-1]
        for i in range(n - 2, -1, -1):
            suf[i] = min(nums[i], suf[i + 1])
        ans = float("-inf")
        pre = 0
        for i in range(n - 1):
            pre += nums[i]
            ans = max(ans, pre - suf[i + 1])
        return int(ans)

    def maximumScore_reverse(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(1)-extra space: walk right-to-left, maintain suffix sum/min,
        and recover prefixSum(i) as total - suffixSum(i+1).

        Algorithm:
        - total = sum(nums); track suffix_sum and suf_min while i decreases.
        - At each valid split i, score = (total - suffix_sum) - suf_min.

        Complexity: O(n) time, O(1) extra space.
        """
        total = sum(nums)
        suf_min = nums[-1]
        suffix_sum = nums[-1]
        ans = float("-inf")
        for i in range(len(nums) - 2, -1, -1):
            ans = max(ans, (total - suffix_sum) - suf_min)
            suf_min = min(suf_min, nums[i])
            suffix_sum += nums[i]
        return int(ans)
# @lc code=end
