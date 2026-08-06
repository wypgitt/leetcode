#
# @lc app=leetcode id=2905 lang=python3
#
# [2905] Find Indices With Index and Value Difference II
#
# https://leetcode.com/problems/find-indices-with-index-and-value-difference-ii/description/
#
# algorithms
# Medium (32.69%)
# Likes:    306
# Dislikes: 11
# Total Accepted:    24.3K
# Total Submissions: 74.2K
# Testcase Example:  "[5,1,4,1]\n2\n4"
#
#
# You are given a 0-indexed integer array nums having length n, an integer
# indexDifference, and an integer valueDifference.
#
# Your task is to find two indices i and j, both in the range [0, n - 1],
# that satisfy the following conditions:
#
# abs(i - j) >= indexDifference, and
#
# abs(nums[i] - nums[j]) >= valueDifference
#
# Return an integer array answer, where answer = [i, j] if there are two
# such indices, and answer = [-1, -1] otherwise. If there are multiple
# choices for the two indices, return any of them.
#
# Note: i and j may be equal.
#
# Example 1:
#
# Input: nums = [5,1,4,1], indexDifference = 2, valueDifference = 4
# Output: [0,3]
# Explanation: In this example, i = 0 and j = 3 can be selected.
# abs(0 - 3) >= 2 and abs(nums[0] - nums[3]) >= 4.
# Hence, a valid answer is [0,3].
# [3,0] is also a valid answer.
#
# Example 2:
#
# Input: nums = [2,1], indexDifference = 0, valueDifference = 0
# Output: [0,0]
# Explanation: In this example, i = 0 and j = 0 can be selected.
# abs(0 - 0) >= 0 and abs(nums[0] - nums[0]) >= 0.
# Hence, a valid answer is [0,0].
# Other valid answers are [0,1], [1,0], and [1,1].
#
# Example 3:
#
# Input: nums = [1,2,3], indexDifference = 2, valueDifference = 4
# Output: [-1,-1]
# Explanation: In this example, it can be shown that it is impossible to
# find two indices that satisfy both conditions.
# Hence, [-1,-1] is returned.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# 0 <= indexDifference <= 10^5
#
# 0 <= valueDifference <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def findIndices(
        self, nums: List[int], indexDifference: int, valueDifference: int
    ) -> List[int]:
        """
        Interview explanation:
        Same as I but n up to 1e5: find i, j with |i-j| >= indexDifference and
        |nums[i]-nums[j]| >= valueDifference.

        Algorithm:
        - Scan j from indexDifference..n-1. Maintain min/max indices among
          0..j-indexDifference; check value gap against nums[j].

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        min_i = max_i = 0
        for j in range(indexDifference, n):
            i = j - indexDifference
            if nums[i] < nums[min_i]:
                min_i = i
            if nums[i] > nums[max_i]:
                max_i = i
            if nums[j] - nums[min_i] >= valueDifference:
                return [min_i, j]
            if nums[max_i] - nums[j] >= valueDifference:
                return [max_i, j]
        return [-1, -1]
# @lc code=end
