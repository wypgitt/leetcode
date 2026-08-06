#
# @lc app=leetcode id=364 lang=python3
#
# [364] Nested List Weight Sum II
#
# https://leetcode.com/problems/nested-list-weight-sum-ii/description/
#
# algorithms
# Medium (67.03%)
# Likes:    1172
# Dislikes: 482
# Total Accepted:    168.8K
# Total Submissions: 251.9K
# Testcase Example:  "[[1,1],2,[1,1]]"
#
#
# You are given a nested list of integers nestedList. Each element is
# either an integer or a list whose elements may also be integers or other
# lists.
#
# The depth of an integer is the number of lists that it is inside of. For
# example, the nested list [1,[2,2],[[3],2],1] has each integer's value
# set to its depth. Let maxDepth be the maximum depth of any integer.
#
# The weight of an integer is maxDepth - (the depth of the integer) + 1.
#
# Return the sum of each integer in nestedList multiplied by its weight.
#
# Example 1:
#
# Input: nestedList = [[1,1],2,[1,1]]
# Output: 8
# Explanation: Four 1's with a weight of 1, one 2 with a weight of 2.
# 1*1 + 1*1 + 2*2 + 1*1 + 1*1 = 8
#
# Example 2:
#
# Input: nestedList = [1,[4,[6]]]
# Output: 17
# Explanation: One 1 at depth 3, one 4 at depth 2, and one 6 at depth 1.
# 1*3 + 4*2 + 6*1 = 17
#
# Constraints:
#
# 1 <= nestedList.length <= 50
#
# The values of the integers in the nested list is in the range [-100,
# 100].
#
# The maximum depth of any integer is less than or equal to 50.
#
# There are no empty lists.
#
# @lc code=start
from collections import deque
from typing import List

# """
# This is the interface that allows for creating nested lists.
# You should not implement it, or speculate about its implementation
# """
# class NestedInteger:
#     def isInteger(self) -> bool: ...
#     def getInteger(self) -> int: ...
#     def getList(self) -> List["NestedInteger"]: ...


class Solution:
    def depthSumInverse(self, nestedList: List[NestedInteger]) -> int:
        """
        Interview explanation:
        Weight is maxDepth - depth + 1. Two-pass DFS: find max depth, then sum
        value * (maxDepth - depth + 1). Or one-pass BFS accumulating unweighted
        sum each level and adding running sum each deeper level.

        Algorithm (single BFS trick):
        - level_sum accumulates all integers seen so far; each new level add
          level_sum again (deeper levels get extra +1 weight retroactively).

        Complexity: O(N) time and space.
        """
        total = 0
        level_sum = 0
        q = deque(nestedList)
        while q:
            for _ in range(len(q)):
                ni = q.popleft()
                if ni.isInteger():
                    level_sum += ni.getInteger()
                else:
                    q.extend(ni.getList())
            total += level_sum
        return total

    def depthSumInverse_dfs(self, nestedList: List[NestedInteger]) -> int:
        """
        Interview explanation:
        Alternate: DFS to find maxDepth, then DFS again weighting by
        maxDepth - depth + 1.

        Complexity: O(N) time and space.
        """
        def max_depth(lst: List[NestedInteger]) -> int:
            depth = 1
            for ni in lst:
                if not ni.isInteger():
                    depth = max(depth, 1 + max_depth(ni.getList()))
            return depth

        def dfs(lst: List[NestedInteger], depth: int, max_d: int) -> int:
            total = 0
            for ni in lst:
                if ni.isInteger():
                    total += ni.getInteger() * (max_d - depth + 1)
                else:
                    total += dfs(ni.getList(), depth + 1, max_d)
            return total

        md = max_depth(nestedList)
        return dfs(nestedList, 1, md)
# @lc code=end
