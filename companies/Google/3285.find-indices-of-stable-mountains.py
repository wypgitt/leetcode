#
# @lc app=leetcode id=3285 lang=python3
#
# [3285] Find Indices of Stable Mountains
#
# https://leetcode.com/problems/find-indices-of-stable-mountains/description/
#
# algorithms
# Easy (87.20%)
# Likes:    112
# Dislikes: 40
# Total Accepted:    74.4K
# Total Submissions: 85.4K
# Testcase Example:  "[1,2,3,4,5]\n2"
#
#
# There are n mountains in a row, and each mountain has a height. You are
# given an integer array height where height[i] represents the height of
# mountain i, and an integer threshold.
#
# A mountain is called stable if the mountain just before it (if it
# exists) has a height strictly greater than threshold. Note that mountain
# 0 is not stable.
#
# Return an array containing the indices of all stable mountains in any
# order.
#
# Example 1:
#
# Input: height = [1,2,3,4,5], threshold = 2
#
# Output: [3,4]
#
# Explanation:
#
# Mountain 3 is stable because height[2] == 3 is greater than threshold ==
# 2.
#
# Mountain 4 is stable because height[3] == 4 is greater than threshold ==
# 2.
#
# Example 2:
#
# Input: height = [10,1,10,1,10], threshold = 3
#
# Output: [1,3]
#
# Example 3:
#
# Input: height = [10,1,10,1,10], threshold = 10
#
# Output: []
#
# Constraints:
#
# 2 <= n == height.length <= 100
#
# 1 <= height[i] <= 100
#
# 1 <= threshold <= 100
#

# @lc code=start
from typing import List


class Solution:
    def stableMountains(self, height: List[int], threshold: int) -> List[int]:
        """
        Interview explanation:
        Mountain i (i>0) is stable iff height[i-1] > threshold.

        Algorithm:
        - Collect every index i>=1 with height[i-1] > threshold.
        - Alternate: list comprehension over range(1, n).

        Complexity: O(n) time, O(n) space for the answer.
        """
        ans = []
        for i in range(1, len(height)):
            if height[i - 1] > threshold:
                ans.append(i)
        return ans

    def stableMountains_comp(self, height: List[int], threshold: int) -> List[int]:
        """
        Interview explanation:
        Same rule as a one-liner comprehension.

        Algorithm:
        - [i for i in range(1, n) if height[i-1] > threshold].

        Complexity: O(n) time, O(n) space.
        """
        return [i for i in range(1, len(height)) if height[i - 1] > threshold]
# @lc code=end
