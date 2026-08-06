#
# @lc app=leetcode id=2574 lang=python3
#
# [2574] Left and Right Sum Differences
#
# https://leetcode.com/problems/left-and-right-sum-differences/description/
#
# algorithms
# Easy (89.67%)
# Likes:    1505
# Dislikes: 121
# Total Accepted:    376.3K
# Total Submissions: 419.7K
# Testcase Example:  "[10,4,8,3]"
#
# You are given a 0-indexed integer array nums of size n.
#
# Define two arrays leftSum and rightSum where:
#
#
# leftSum[i] is the sum of elements to the left of the index i in the array
# nums. If there is no such element, leftSum[i] = 0.
#
#
# rightSum[i] is the sum of elements to the right of the index i in the array
# nums. If there is no such element, rightSum[i] = 0.
#
# Return an integer array answer of size n where answer[i] = |leftSum[i] -
# rightSum[i]|.
#
#
#
# Example 1:
#
# Input: nums = [10,4,8,3]
# Output: [15,1,11,22]
# Explanation: The array leftSum is [0,10,14,22] and the array rightSum is
# [15,11,3,0].
# The array answer is [|0 - 15|,|10 - 11|,|14 - 3|,|22 - 0|] = [15,1,11,22].
#
# Example 2:
#
# Input: nums = [1]
# Output: [0]
# Explanation: The array leftSum is [0] and the array rightSum is [0].
# The array answer is [|0 - 0|] = [0].
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def leftRightDifference(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        For each i, answer |leftSum[i] - rightSum[i]|.

        Algorithm:
        - Track running left sum and total-as-right; one pass.

        Complexity: O(n) time, O(1) extra space.
        """
        total = sum(nums)
        left = 0
        ans = []
        for x in nums:
            total -= x
            ans.append(abs(left - total))
            left += x
        return ans
# @lc code=end
