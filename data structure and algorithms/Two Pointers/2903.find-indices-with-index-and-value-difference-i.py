#
# @lc app=leetcode id=2903 lang=python3
#
# [2903] Find Indices With Index and Value Difference I
#
# https://leetcode.com/problems/find-indices-with-index-and-value-difference-i/description/
#
# algorithms
# Easy (60.04%)
# Likes:    171
# Dislikes: 18
# Total Accepted:    56.6K
# Total Submissions: 94.2K
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
# 1 <= n == nums.length <= 100
#
# 0 <= nums[i] <= 50
#
# 0 <= indexDifference <= 100
#
# 0 <= valueDifference <= 50
#

# @lc code=start
from typing import List


class Solution:
    def findIndices(
        self, nums: List[int], indexDifference: int, valueDifference: int
    ) -> List[int]:
        """
        Interview explanation:
        Find any i, j with |i-j| >= indexDifference and
        |nums[i]-nums[j]| >= valueDifference (i may equal j).

        Algorithm:
        - Brute force all pairs (n <= 100).

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(nums)
        for i in range(n):
            for j in range(n):
                if abs(i - j) >= indexDifference and abs(
                    nums[i] - nums[j]
                ) >= valueDifference:
                    return [i, j]
        return [-1, -1]

    def findIndices_track(
        self, nums: List[int], indexDifference: int, valueDifference: int
    ) -> List[int]:
        """
        Interview explanation:
        Same pair constraints; maintain the min/max index in the left window
        that is at least indexDifference away from j.

        Algorithm:
        - Scan j from indexDifference..n-1; update min_i/max_i at i=j-indexDifference;
          return when valueDifference vs min or max is met.

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
