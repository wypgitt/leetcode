#
# @lc app=leetcode id=339 lang=python3
#
# [339] Nested List Weight Sum
#
# https://leetcode.com/problems/nested-list-weight-sum/description/
#
# algorithms
# Medium (85.98%)
# Likes:    1875
# Dislikes: 487
# Total Accepted:    418.5K
# Total Submissions: 486.8K
# Testcase Example:  "[[1,1],2,[1,1]]"
#
#
# You are given a nested list of integers nestedList. Each element is
# either an integer or a list whose elements may also be integers or other
# lists.
#
# The depth of an integer is the number of lists that it is inside of. For
# example, the nested list [1,[2,2],[[3],2],1] has each integer's value
# set to its depth.
#
# Return the sum of each integer in nestedList multiplied by its depth.
#
# Example 1:
#
# Input: nestedList = [[1,1],2,[1,1]]
# Output: 10
# Explanation: Four 1's at depth 2, one 2 at depth 1. 1*2 + 1*2 + 2*1 +
# 1*2 + 1*2 = 10.
#
# Example 2:
#
# Input: nestedList = [1,[4,[6]]]
# Output: 27
# Explanation: One 1 at depth 1, one 4 at depth 2, and one 6 at depth 3.
# 1*1 + 4*2 + 6*3 = 27.
#
# Example 3:
#
# Input: nestedList = [0]
# Output: 0
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
    def depthSum(self, nestedList: List[NestedInteger]) -> int:
        """
        Interview explanation:
        DFS: each integer contributes value * depth; nested lists recurse at
        depth + 1. Depth of the outermost list is 1.

        Algorithm:
        - dfs(list, depth): sum int*depth or recurse into nested lists.

        Complexity: O(N) time/space for N nested integers.
        """
        def dfs(lst: List[NestedInteger], depth: int) -> int:
            total = 0
            for ni in lst:
                if ni.isInteger():
                    total += ni.getInteger() * depth
                else:
                    total += dfs(ni.getList(), depth + 1)
            return total

        return dfs(nestedList, 1)

    def depthSum_bfs(self, nestedList: List[NestedInteger]) -> int:
        """
        Interview explanation:
        Alternate: BFS by level; multiply each integer by current depth, enqueue
        nested lists for the next level.

        Algorithm:
        - Queue of NestedInteger; depth starts at 1; process level by level.

        Complexity: O(N) time and space.
        """
        q = deque(nestedList)
        depth = 1
        total = 0
        while q:
            for _ in range(len(q)):
                ni = q.popleft()
                if ni.isInteger():
                    total += ni.getInteger() * depth
                else:
                    q.extend(ni.getList())
            depth += 1
        return total
# @lc code=end
