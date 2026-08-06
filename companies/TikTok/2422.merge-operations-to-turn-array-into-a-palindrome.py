#
# @lc app=leetcode id=2422 lang=python3
#
# [2422] Merge Operations to Turn Array Into a Palindrome
#
# https://leetcode.com/problems/merge-operations-to-turn-array-into-a-palindrome/description/
#
# algorithms
# Medium (68.84%)
# Likes:    154
# Dislikes: 16
# Total Accepted:    19.3K
# Total Submissions: 28K
# Testcase Example:  "[4,3,2,1,2,3,1]"
#
#
# You are given an array nums consisting of positive integers.
#
# You can perform the following operation on the array any number of
# times:
#
# Choose any two adjacent elements and replace them with their sum.
#
# For example, if nums = [1,2,3,1], you can apply one operation to make it
# [1,5,1].
#
# Return the minimum number of operations needed to turn the array into a
# palindrome.
#
# Example 1:
#
# Input: nums = [4,3,2,1,2,3,1]
# Output: 2
# Explanation: We can turn the array into a palindrome in 2 operations as
# follows:
# - Apply the operation on the fourth and fifth element of the array, nums
# becomes equal to [4,3,2,3,3,1].
# - Apply the operation on the fifth and sixth element of the array, nums
# becomes equal to [4,3,2,3,4].
# The array [4,3,2,3,4] is a palindrome.
# It can be shown that 2 is the minimum number of operations needed.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 3
# Explanation: We do the operation 3 times in any position, we obtain the
# array [10] at the end which is a palindrome.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# @lc code=start
from typing import List


class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Merge adjacent elements (replace two with their sum) to make the
        array a palindrome; return min merges.

        Algorithm:
        - Two pointers: if ends equal, advance both; else merge the smaller side
          into neighbor (+1 op) and continue.

        Complexity: O(n) time, O(1) space.
        """
        i, j = 0, len(nums) - 1
        ops = 0
        left, right = nums[i], nums[j]
        while i < j:
            if left == right:
                i += 1
                j -= 1
                if i < j:
                    left, right = nums[i], nums[j]
            elif left < right:
                i += 1
                left += nums[i]
                ops += 1
            else:
                j -= 1
                right += nums[j]
                ops += 1
        return ops

    def minimumOperations_two_pointers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate two-pointer with mutable running sums (same greedy).

        Algorithm:
        - Same as primary.

        Complexity: O(n) time, O(1) space.
        """
        return self.minimumOperations(nums)
# @lc code=end
