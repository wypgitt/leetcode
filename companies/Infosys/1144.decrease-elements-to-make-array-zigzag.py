#
# @lc app=leetcode id=1144 lang=python3
#
# [1144] Decrease Elements To Make Array Zigzag
#
# https://leetcode.com/problems/decrease-elements-to-make-array-zigzag/description/
#
# algorithms
# Medium (49.42%)
# Likes:    466
# Dislikes: 169
# Total Accepted:    26.7K
# Total Submissions: 54.0K
# Testcase Example:  "[1,2,3]"
#
# Given an array nums of integers, a move consists of choosing any element and
# decreasing it by 1.
#
# An array A is a zigzag array if either:
#
# Every even-indexed element is greater than adjacent elements, ie. A[0] > A[1]
# < A[2] > A[3] < A[4] > ...
#
# OR, every odd-indexed element is greater than adjacent elements, ie. A[0] <
# A[1] > A[2] < A[3] > A[4] < ...
#
# Return the minimum number of moves to transform the given array nums into a
# zigzag array.
#
# Example 1:
#
# Input: nums = [1,2,3]
# Output: 2
# Explanation: We can decrease 2 to 0 or 3 to 1.
#
# Example 2:
#
# Input: nums = [9,6,1,6,2]
# Output: 4
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def movesToMakeZigzag(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Make nums zigzag by only decreasing elements: either nums[even] < neighbors
        or nums[odd] < neighbors. Choose the cheaper of the two patterns; for each
        peak position, decrease just enough vs left/right.

        Algorithm:
        - For pattern p in {0,1} (which indices are valleys): for each valley i,
          need nums[i] < neighbors → moves += max(0, nums[i] - min(neigh) + 1).
        - Return min of both patterns.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)

        def cost(valley: int) -> int:
            moves = 0
            for i in range(valley, n, 2):
                left = nums[i - 1] if i > 0 else float("inf")
                right = nums[i + 1] if i + 1 < n else float("inf")
                need = min(left, right) - 1
                if nums[i] > need:
                    moves += nums[i] - need
            return moves

        return min(cost(0), cost(1))
# @lc code=end
