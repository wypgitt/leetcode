#
# @lc app=leetcode id=3523 lang=python3
#
# [3523] Make Array Non-decreasing
#
# https://leetcode.com/problems/make-array-non-decreasing/description/
#
# algorithms
# Medium (57.70%)
# Likes:    97
# Dislikes: 9
# Total Accepted:    34.6K
# Total Submissions: 60K
# Testcase Example:  "[4,2,5,3,5]"
#
#
# You are given an integer array nums. In one operation, you can select a
# subarray and replace it with a single element equal to its maximum
# value.
#
# Return the maximum possible size of the array after performing zero or
# more operations such that the resulting array is non-decreasing.
#
# Example 1:
#
# Input: nums = [4,2,5,3,5]
#
# Output: 3
#
# Explanation:
#
# One way to achieve the maximum size is:
#
# Replace subarray nums[1..2] = [2, 5] with 5 → [4, 5, 3, 5].
#
# Replace subarray nums[2..3] = [3, 5] with 5 → [4, 5, 5].
#
# The final array [4, 5, 5] is non-decreasing with size 3.
#
# Example 2:
#
# Input: nums = [1,2,3]
#
# Output: 3
#
# Explanation:
#
# No operation is needed as the array [1,2,3] is already non-decreasing.
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^5
#
# 1 <= nums[i] <= 2 * 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maximumPossibleSize(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Merging a subarray into its max means kept values are maxima of contiguous
        blocks. To maximize blocks that stay non-decreasing, greedily keep the next
        value that is ≥ the last kept value; smaller values can always be absorbed.

        Algorithm:
        - Scan left to right; whenever nums[i] ≥ last kept, keep it and update last.
        - Answer is the keep count.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        last = 0
        for x in nums:
            if x >= last:
                ans += 1
                last = x
        return ans

    def maximumPossibleSize_stack(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: build the kept non-decreasing sequence explicitly.

        Algorithm:
        - Append nums[i] when empty or ≥ stack top; length is the answer.

        Complexity: O(n) time, O(n) space.
        """
        stack: List[int] = []
        for x in nums:
            if not stack or x >= stack[-1]:
                stack.append(x)
        return len(stack)
# @lc code=end
