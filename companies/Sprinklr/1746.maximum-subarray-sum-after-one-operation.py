#
# @lc app=leetcode id=1746 lang=python3
#
# [1746] Maximum Subarray Sum After One Operation
#
# https://leetcode.com/problems/maximum-subarray-sum-after-one-operation/description/
#
# algorithms
# Medium (65.24%)
# Likes:    314
# Dislikes: 10
# Total Accepted:    14.1K
# Total Submissions: 21.6K
# Testcase Example:  "[2,-1,-4,-3]"
#
#
# You are given an integer array nums. You must perform exactly one
# operation where you can replace one element nums[i] with nums[i] *
# nums[i].
#
#
#
# Return the maximum possible subarray sum after exactly one operation.
# The subarray must be non-empty.
#
#
#
#
#
# Example 1:
#
#
#
#
# Input: nums = [2,-1,-4,-3]
# Output: 17
# Explanation: You can perform the operation on index 2 (0-indexed) to
# make nums = [2,-1,16,-3]. Now, the maximum subarray sum is 2 + -1 + 16 =
# 17.
#
#
#
# Example 2:
#
#
#
#
# Input: nums = [1,-1,1,1,-1,-1,1]
# Output: 4
# Explanation: You can perform the operation on index 1 (0-indexed) to
# make nums = [1,1,1,1,-1,-1,1]. Now, the maximum subarray sum is 1 + 1 +
# 1 + 1 = 4.
#
#
#
#
#
# Constraints:
#
#
#
#
#
# 1 <= nums.length <= 10^5
#
#
# -10^4 <= nums[i] <= 10^4
#
# @lc code=start
from typing import List


class Solution:
    def maxSumAfterOperation(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Maximize a subarray sum after replacing at most one element by
        its square. Keep two Kadane states: without using the square yet, and
        after having used it.

        Algorithm:
        - no = max ending here without square
        - yes = max ending here with square already used
        - Track global max of both states.

        Complexity: O(n) time, O(1) space.
        """
        no = nums[0]
        yes = nums[0] * nums[0]
        ans = max(no, yes)
        for i in range(1, len(nums)):
            x = nums[i]
            new_no = max(x, no + x)
            new_yes = max(x * x, no + x * x, yes + x)
            no, yes = new_no, new_yes
            ans = max(ans, no, yes)
        return ans
# @lc code=end
