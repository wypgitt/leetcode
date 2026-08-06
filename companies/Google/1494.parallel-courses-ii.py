#
# @lc app=leetcode id=1494 lang=python3
#
# [1494] Parallel Courses II
#
# https://leetcode.com/problems/parallel-courses-ii/description/
#
# algorithms
# Hard (31.25%)
# Likes:    1159
# Dislikes: 78
# Total Accepted:    28.8K
# Total Submissions: 92.2K
# Testcase Example:  "4"
#
# You are given an integer n, which indicates that there are n courses labeled
# from 1 to n. You are also given an array relations where relations[i] =
# [prevCourse_i, nextCourse_i], representing a prerequisite relationship
# between course prevCourse_i and course nextCourse_i: course prevCourse_i has
# to be taken before course nextCourse_i. Also, you are given the integer k.
#
# In one semester, you can take at most k courses as long as you have taken all
# the prerequisites in the previous semesters for the courses you are taking.
#
# Return the minimum number of semesters needed to take all courses. The
# testcases will be generated such that it is possible to take every course.
#
# Example 1:
#
# Input: n = 4, relations = [[2,1],[3,1],[1,4]], k = 2
# Output: 3
# Explanation: The figure above represents the given graph.
# In the first semester, you can take courses 2 and 3.
# In the second semester, you can take course 1.
# In the third semester, you can take course 4.
#
# Example 2:
#
# Input: n = 5, relations = [[2,1],[3,1],[4,1],[1,5]], k = 2
# Output: 4
# Explanation: The figure above represents the given graph.
# In the first semester, you can only take courses 2 and 3 since you cannot
# take more than two per semester.
# In the second semester, you can take course 4.
# In the third semester, you can take course 1.
# In the fourth semester, you can take course 5.
#
# Constraints:
#
# 1 <= n <= 15
#
# 1 <= k <= n
#
# 0 <= relations.length <= n * (n-1) / 2
#
# relations[i].length == 2
#
# 1 <= prevCourse_i, nextCourse_i <= n
#
# prevCourse_i != nextCourse_i
#
# All the pairs [prevCourse_i, nextCourse_i] are unique.
#
# The given graph is a directed acyclic graph.
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def minNumberOfSemesters(self, n: int, relations: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Take at most k courses per semester with prerequisites. Bitmask DP on
        the set of completed courses; from a mask, find courses with prereqs
        satisfied and try all subsets of size ≤k.

        Algorithm:
        - prereq[v] bitmask; dp(mask): if mask==(1<<n)-1 return 0; compute
          can_take; enumerate submasks of can_take with popcount≤k; 1+dp(new).

        Complexity: O(3^n) / O(2^n * C) with submask enum; n≤15.
        """
        pre = [0] * n
        for a, b in relations:
            pre[b - 1] |= 1 << (a - 1)
        full = (1 << n) - 1

        @lru_cache(None)
        def dp(mask):
            if mask == full:
                return 0
            can = 0
            for i in range(n):
                if (mask & (1 << i)) == 0 and (pre[i] & mask) == pre[i]:
                    can |= 1 << i
            # enumerate non-empty subsets of can with size <= k
            best = n + 1
            sub = can
            while sub:
                if bin(sub).count("1") <= k:
                    best = min(best, 1 + dp(mask | sub))
                sub = (sub - 1) & can
            return best

        return dp(0)
# @lc code=end
