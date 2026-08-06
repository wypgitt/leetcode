#
# @lc app=leetcode id=3397 lang=python3
#
# [3397] Maximum Number of Distinct Elements After Operations
#
# https://leetcode.com/problems/maximum-number-of-distinct-elements-after-operations/description/
#
# algorithms
# Medium (52.11%)
# Likes:    570
# Dislikes: 22
# Total Accepted:    104.6K
# Total Submissions: 200.7K
# Testcase Example:  "[1,2,2,3,3,4]\n2"
#
#
# You are given an integer array nums and an integer k.
#
# You are allowed to perform the following operation on each element of
# the array at most once:
#
# Add an integer in the range [-k, k] to the element.
#
# Return the maximum possible number of distinct elements in nums after
# performing the operations.
#
# Example 1:
#
# Input: nums = [1,2,2,3,3,4], k = 2
#
# Output: 6
#
# Explanation:
#
# nums changes to [-1, 0, 1, 2, 3, 4] after performing operations on the
# first four elements.
#
# Example 2:
#
# Input: nums = [4,4,4,4], k = 1
#
# Output: 3
#
# Explanation:
#
# By adding -1 to nums[0] and 1 to nums[1], nums changes to [3, 5, 4, 4].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 0 <= k <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maxDistinctElements(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Each value may move into [x-k, x+k]. Greedily assign the smallest still
        available integer in that range to maximize distinct count.

        Algorithm:
        - Sort nums; keep prev = last assigned value.
        - For x, take cand = max(x-k, prev+1); accept if cand <= x+k.

        Complexity: O(n log n) time, O(1) extra space (sort in place).
        """
        nums.sort()
        ans = 0
        prev = float('-inf')
        for x in nums:
            cand = max(x - k, prev + 1)
            if cand <= x + k:
                ans += 1
                prev = cand
        return ans
# @lc code=end
