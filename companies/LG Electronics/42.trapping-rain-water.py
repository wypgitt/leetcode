#
# @lc app=leetcode id=42 lang=python3
#
# [42] Trapping Rain Water
#
# https://leetcode.com/problems/trapping-rain-water/description/
#
# algorithms
# Hard (67.94%)
# Likes:    36868
# Dislikes: 711
# Total Accepted:    3.8M
# Total Submissions: 5.6M
# Testcase Example:  "[0,1,0,2,1,0,1,3,2,1,2,1]"
#
# Given n non-negative integers representing an elevation map where the width
# of each bar is 1, compute how much water it can trap after raining.
#
# Example 1:
#
# Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
# Output: 6
# Explanation: The above elevation map (black section) is represented by array
# [0,1,0,2,1,0,1,3,2,1,2,1]. In this case, 6 units of rain water (blue section)
# are being trapped.
#
# Example 2:
#
# Input: height = [4,2,0,3,2,5]
# Output: 9
#
# Constraints:
#
# n == height.length
#
# 1 <= n <= 2 * 10^4
#
# 0 <= height[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def trap(self, height: List[int]) -> int:
        """
        Interview explanation:
        Water at each index is min(left_max, right_max) - height. Two pointers
        advance the side with the smaller running max, because that side's
        water is already determined by its own max.

        Algorithm:
        - left/right pointers with left_max/right_max.
        - If left_max <= right_max, water at left is left_max - height[left];
          advance left. Symmetric for right.

        Complexity: O(n) time, O(1) space.
        """
        return self.trap_two_pointers(height)

    def trap_two_pointers(self, height: List[int]) -> int:
        """
        Interview explanation:
        Optimal O(1)-space two-pointer scan (same as primary).

        Algorithm:
        - Maintain left_max and right_max; always process the shorter bound.

        Complexity: O(n) time, O(1) space.
        """
        n = len(height)
        if n < 3:
            return 0

        left, right = 0, n - 1
        left_max = right_max = 0
        water = 0

        while left < right:
            if height[left] <= height[right]:
                if height[left] >= left_max:
                    left_max = height[left]
                else:
                    water += left_max - height[left]
                left += 1
            else:
                if height[right] >= right_max:
                    right_max = height[right]
                else:
                    water += right_max - height[right]
                right -= 1

        return water

    def trap_stack(self, height: List[int]) -> int:
        """
        Interview explanation:
        Monotonic decreasing stack of indices. When a taller bar appears, it
        forms a right bound for trapped water with earlier bars.

        Algorithm:
        - While stack not empty and height[i] > height[stack.top]:
          - Pop bottom; if stack empty, break.
          - Bounded water = (min(height[i], height[stack.top]) - bottom)
            * width between stack.top and i.
        - Push i.

        Complexity: O(n) time, O(n) space.
        """
        stack: List[int] = []
        water = 0
        for i, h in enumerate(height):
            while stack and h > height[stack[-1]]:
                bottom = height[stack.pop()]
                if not stack:
                    break
                left = stack[-1]
                water += (min(h, height[left]) - bottom) * (i - left - 1)
            stack.append(i)
        return water

    def trap_prefix(self, height: List[int]) -> int:
        """
        Interview explanation:
        Precompute left_max[i] and right_max[i], then sum
        min(left_max[i], right_max[i]) - height[i].

        Algorithm:
        - Forward pass for left maxima; backward for right maxima.
        - Accumulate trapped water at each index.

        Complexity: O(n) time, O(n) space.
        """
        n = len(height)
        if n < 3:
            return 0

        left_max = [0] * n
        right_max = [0] * n
        left_max[0] = height[0]
        right_max[-1] = height[-1]

        for i in range(1, n):
            left_max[i] = max(left_max[i - 1], height[i])
        for i in range(n - 2, -1, -1):
            right_max[i] = max(right_max[i + 1], height[i])

        return sum(
            min(left_max[i], right_max[i]) - height[i] for i in range(n)
        )
# @lc code=end
