#
# @lc app=leetcode id=997 lang=python3
#
# [997] Find the Town Judge
#
# https://leetcode.com/problems/find-the-town-judge/description/
#
# algorithms
# Easy (51.0%)
# Likes:    7023
# Dislikes: 635
# Total Accepted:    777K
# Total Submissions: 1.5M
# Testcase Example:  "2"
#
# In a town, there are n people labeled from 1 to n. There is a rumor that one
# of these people is secretly the town judge.
#
# If the town judge exists, then:
#
# The town judge trusts nobody.
#
# Everybody (except for the town judge) trusts the town judge.
#
# There is exactly one person that satisfies properties 1 and 2.
#
# You are given an array trust where trust[i] = [a_i, b_i] representing that
# the person labeled a_i trusts the person labeled b_i. If a trust relationship
# does not exist in trust array, then such a trust relationship does not exist.
#
# Return the label of the town judge if the town judge exists and can be
# identified, or return -1 otherwise.
#
# Example 1:
#
# Input: n = 2, trust = [[1,2]]
# Output: 2
#
# Example 2:
#
# Input: n = 3, trust = [[1,3],[2,3]]
# Output: 3
#
# Example 3:
#
# Input: n = 3, trust = [[1,3],[2,3],[3,1]]
# Output: -1
#
# Constraints:
#
# 1 <= n <= 1000
#
# 0 <= trust.length <= 10^4
#
# trust[i].length == 2
#
# All the pairs of trust are unique.
#
# a_i != b_i
#
# 1 <= a_i, b_i <= n
#

# @lc code=start
from typing import List


class Solution:
    def findJudge(self, n: int, trust: List[List[int]]) -> int:
        """
        Interview explanation:
        Judge has out-degree 0 and in-degree n-1. Score[i] += 1 when trusted,
        -= 1 when trusts; judge's score is n-1.

        Algorithm:
        - score = [0]*(n+1). For a->b: score[a]-=1; score[b]+=1.
        - Return i with score[i]==n-1, else -1.

        Complexity: O(n + t) time, O(n) space.
        """
        score = [0] * (n + 1)
        for a, b in trust:
            score[a] -= 1
            score[b] += 1
        for i in range(1, n + 1):
            if score[i] == n - 1:
                return i
        return -1
# @lc code=end
