#
# @lc app=leetcode id=1743 lang=python3
#
# [1743] Restore the Array From Adjacent Pairs
#
# https://leetcode.com/problems/restore-the-array-from-adjacent-pairs/description/
#
# algorithms
# Medium (75.11%)
# Likes:    2061
# Dislikes: 71
# Total Accepted:    131K
# Total Submissions: 174K
# Testcase Example:  "[[2,1],[3,4],[3,2]]"
#
# There is an integer array nums that consists of n unique elements, but you
# have forgotten it. However, you do remember every pair of adjacent elements
# in nums.
#
# You are given a 2D integer array adjacentPairs of size n - 1 where each
# adjacentPairs[i] = [u_i, v_i] indicates that the elements u_i and v_i are
# adjacent in nums.
#
# It is guaranteed that every adjacent pair of elements nums[i] and nums[i+1]
# will exist in adjacentPairs, either as [nums[i], nums[i+1]] or [nums[i+1],
# nums[i]]. The pairs can appear in any order.
#
# Return the original array nums. If there are multiple solutions, return any
# of them.
#
# Example 1:
#
# Input: adjacentPairs = [[2,1],[3,4],[3,2]]
# Output: [1,2,3,4]
# Explanation: This array has all its adjacent pairs in adjacentPairs.
# Notice that adjacentPairs[i] may not be in left-to-right order.
#
# Example 2:
#
# Input: adjacentPairs = [[4,-2],[1,4],[-3,1]]
# Output: [-2,4,1,-3]
# Explanation: There can be negative numbers.
# Another solution is [-3,1,4,-2], which would also be accepted.
#
# Example 3:
#
# Input: adjacentPairs = [[100000,-100000]]
# Output: [100000,-100000]
#
# Constraints:
#
# nums.length == n
#
# adjacentPairs.length == n - 1
#
# adjacentPairs[i].length == 2
#
# 2 <= n <= 10^5
#
# -10^5 <= nums[i], u_i, v_i <= 10^5
#
# There exists some nums that has adjacentPairs as its pairs.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def restoreArray(self, adjacentPairs: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Adjacent pairs describe a path; endpoints have degree 1. Start at an
        endpoint and walk uniquely to rebuild the array.

        Algorithm:
        - Build adjacency; find degree-1 start; iterative walk avoiding previous.

        Complexity: O(n) time, O(n) space.
        """
        g = defaultdict(list)
        for a, b in adjacentPairs:
            g[a].append(b)
            g[b].append(a)
        start = next(x for x, nei in g.items() if len(nei) == 1)
        ans = [start]
        prev = None
        cur = start
        while True:
            nxts = [x for x in g[cur] if x != prev]
            if not nxts:
                break
            prev, cur = cur, nxts[0]
            ans.append(cur)
        return ans
# @lc code=end
