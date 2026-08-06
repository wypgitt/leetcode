#
# @lc app=leetcode id=3740 lang=python3
#
# [3740] Minimum Distance Between Three Equal Elements I
#
# https://leetcode.com/problems/minimum-distance-between-three-equal-elements-i/description/
#
# algorithms
# Easy (73.41%)
# Likes:    313
# Dislikes: 24
# Total Accepted:    147.5K
# Total Submissions: 201K
# Testcase Example:  "[1,2,1,1,3]"
#
#
# You are given an integer array nums.
#
# A tuple (i, j, k) of 3 distinct indices is good if nums[i] == nums[j] ==
# nums[k].
#
# The distance of a good tuple is abs(i - j) + abs(j - k) + abs(k - i),
# where abs(x) denotes the absolute value of x.
#
# Return an integer denoting the minimum possible distance of a good
# tuple. If no good tuples exist, return -1.
#
# Example 1:
#
# Input: nums = [1,2,1,1,3]
#
# Output: 6
#
# Explanation:
#
# The minimum distance is achieved by the good tuple (0, 2, 3).
#
# (0, 2, 3) is a good tuple because nums[0] == nums[2] == nums[3] == 1.
# Its distance is abs(0 - 2) + abs(2 - 3) + abs(3 - 0) = 2 + 1 + 3 = 6.
#
# Example 2:
#
# Input: nums = [1,1,2,3,2,1,2]
#
# Output: 8
#
# Explanation:
#
# The minimum distance is achieved by the good tuple (2, 4, 6).
#
# (2, 4, 6) is a good tuple because nums[2] == nums[4] == nums[6] == 2.
# Its distance is abs(2 - 4) + abs(4 - 6) + abs(6 - 2) = 2 + 2 + 4 = 8.
#
# Example 3:
#
# Input: nums = [1]
#
# Output: -1
#
# Explanation:
#
# There are no good tuples. Therefore, the answer is -1.
#
# Constraints:
#
# 1 <= n == nums.length <= 100
#
# 1 <= nums[i] <= n
#

# @lc code=start
from collections import defaultdict
from math import inf
from typing import List


class Solution:
    def minimumDistance(self, nums: List[int]) -> int:
        """
        Interview explanation:
        For i < j < k, abs(i-j)+abs(j-k)+abs(k-i) = 2*(k-i). Minimize the span
        of any three equal values; answer is twice that span.

        Algorithm:
        - Group indices by value; for each list, minimize idxs[t+2]-idxs[t].
        - Return 2 * that minimum, or -1.

        Complexity: O(n) time, O(n) space.
        """
        pos = defaultdict(list)
        for i, x in enumerate(nums):
            pos[x].append(i)
        best = inf
        for idxs in pos.values():
            for t in range(len(idxs) - 2):
                best = min(best, idxs[t + 2] - idxs[t])
        return -1 if best is inf else 2 * best

    def minimumDistance_brute(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: O(n^3) enumerate triples (n <= 100).

        Algorithm:
        - For all i < j < k with equal values, track min distance.

        Complexity: O(n^3) time, O(1) space.
        """
        n = len(nums)
        ans = inf
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    if nums[i] == nums[j] == nums[k]:
                        ans = min(ans, 2 * (k - i))
        return -1 if ans is inf else ans
# @lc code=end

