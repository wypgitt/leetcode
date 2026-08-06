#
# @lc app=leetcode id=3741 lang=python3
#
# [3741] Minimum Distance Between Three Equal Elements II
#
# https://leetcode.com/problems/minimum-distance-between-three-equal-elements-ii/description/
#
# algorithms
# Medium (74.70%)
# Likes:    304
# Dislikes: 9
# Total Accepted:    131.6K
# Total Submissions: 176.1K
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
# 1 <= n == nums.length <= 10^5
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
        Same identity as the easy version: distance = 2*(k-i) for i < j < k.
        With n <= 1e5, scan three consecutive occurrences per value.

        Algorithm:
        - Collect positions per value; minimize idxs[t+2] - idxs[t].
        - Answer is twice the minimum span, or -1.

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

    def minimumDistance_rolling(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: keep only the last three indices per value while scanning.

        Algorithm:
        - For each value, maintain a deque of size <= 3; update best on size 3.

        Complexity: O(n) time, O(n) space worst case for the map.
        """
        from collections import deque

        last = defaultdict(deque)
        best = inf
        for i, x in enumerate(nums):
            dq = last[x]
            dq.append(i)
            if len(dq) > 3:
                dq.popleft()
            if len(dq) == 3:
                best = min(best, dq[-1] - dq[0])
        return -1 if best is inf else 2 * best
# @lc code=end

