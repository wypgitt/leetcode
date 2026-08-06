#
# @lc app=leetcode id=3730 lang=python3
#
# [3730] Maximum Calories Burnt from Jumps
#
# https://leetcode.com/problems/maximum-calories-burnt-from-jumps/description/
#
# algorithms
# Medium (72.19%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    872
# Total Submissions: 1.2K
# Testcase Example:  "[1,7,9]"
#
#
# You are given an integer array heights of size n, where heights[i]
# represents the height of the i^th block in an exercise routine.
#
# You start on the ground (height 0) and must jump onto each block exactly
# once in any order.
#
# The calories burned for a jump from a block of height a to a block of
# height b is (a - b)^2.
#
# The calories burned for the first jump from the ground to the chosen
# first block heights[i] is (0 - heights[i])^2.
#
# Return the maximum total calories you can burn by selecting an optimal
# jumping sequence.
#
# Note: Once you jump onto the first block, you cannot return to the
# ground.
#
# Example 1:
#
# Input: heights = [1,7,9]
#
# Output: 181
#
# Explanation:​​​​​​​
#
# The optimal sequence is [9, 1, 7].
#
# Initial jump from the ground to heights[2] = 9: (0 - 9)^2 = 81.
#
# Next jump to heights[0] = 1: (9 - 1)^2 = 64.
#
# Final jump to heights[1] = 7: (1 - 7)^2 = 36.
#
# Total calories burned = 81 + 64 + 36 = 181.
#
# Example 2:
#
# Input: heights = [5,2,4]
#
# Output: 38
#
# Explanation:
#
# The optimal sequence is [5, 2, 4].
#
# Initial jump from the ground to heights[0] = 5: (0 - 5)^2 = 25.
#
# Next jump to heights[1] = 2: (5 - 2)^2 = 9.
#
# Final jump to heights[2] = 4: (2 - 4)^2 = 4.
#
# Total calories burned = 25 + 9 + 4 = 38.
#
# Example 3:
#
# Input: heights = [3,3]
#
# Output: 9
#
# Explanation:
#
# The optimal sequence is [3, 3].
#
# Initial jump from the ground to heights[0] = 3: (0 - 3)^2 = 9.
#
# Next jump to heights[1] = 3: (3 - 3)^2 = 0.
#
# Total calories burned = 9 + 0 = 9.
#
# Constraints:
#
# 1 <= n == heights.length <= 10^5
#
# 1 <= heights[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxCaloriesBurnt(self, heights: List[int]) -> int:
        """
        Interview explanation:
        Calories are squared height gaps. Maximize by alternating highest and
        lowest unused blocks after leaving ground (start with a high jump).

        Algorithm:
        - Sort heights; two pointers: jump to high, then low, updating previous.
        - Finish with the middle element if n is odd.

        Complexity: O(n log n) time, O(n) space for sort.
        """
        heights.sort()
        pre = ans = 0
        l, r = 0, len(heights) - 1
        while l < r:
            ans += (heights[r] - pre) ** 2
            ans += (heights[l] - heights[r]) ** 2
            pre = heights[l]
            l += 1
            r -= 1
        ans += (heights[r] - pre) ** 2
        return ans

    def maxCaloriesBurnt_sequence(self, heights: List[int]) -> int:
        """
        Interview explanation:
        Alternate: materialize the jump order (max, min, max, min, ...) then score.

        Algorithm:
        - Sort; emit highs from the right and lows from the left interleaved.
        - Sum squared differences along 0 -> order.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(heights)
        order = []
        l, r = 0, len(a) - 1
        while l <= r:
            order.append(a[r])
            r -= 1
            if l <= r:
                order.append(a[l])
                l += 1
        pre = ans = 0
        for h in order:
            ans += (h - pre) ** 2
            pre = h
        return ans
# @lc code=end

