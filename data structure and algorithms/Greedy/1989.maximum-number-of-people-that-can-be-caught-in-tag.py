#
# @lc app=leetcode id=1989 lang=python3
#
# [1989] Maximum Number of People That Can Be Caught in Tag
#
# https://leetcode.com/problems/maximum-number-of-people-that-can-be-caught-in-tag/description/
#
# algorithms
# Medium (49.71%)
# Likes:    76
# Dislikes: 11
# Total Accepted:    2.9K
# Total Submissions: 5.8K
# Testcase Example:  "[0,1,0,1,0]\n3"
#
#
# You are playing a game of tag with your friends. In tag, people are
# divided into two teams: people who are "it", and people who are not
# "it". The people who are "it" want to catch as many people as possible
# who are not "it".
#
# You are given a 0-indexed integer array team containing only zeros
# (denoting people who are not "it") and ones (denoting people who are
# "it"), and an integer dist. A person who is "it" at index i can catch
# any one person whose index is in the range [i - dist, i + dist]
# (inclusive) and is not "it".
#
# Return the maximum number of people that the people who are "it" can
# catch.
#
# Example 1:
#
# Input: team = [0,1,0,1,0], dist = 3
# Output: 2
# Explanation:
# The person who is "it" at index 1 can catch people in the range [i-dist,
# i+dist] = [1-3, 1+3] = [-2, 4].
# They can catch the person who is not "it" at index 2.
# The person who is "it" at index 3 can catch people in the range [i-dist,
# i+dist] = [3-3, 3+3] = [0, 6].
# They can catch the person who is not "it" at index 0.
# The person who is not "it" at index 4 will not be caught because the
# people at indices 1 and 3 are already catching one person.
#
# Example 2:
#
# Input: team = [1], dist = 1
# Output: 0
# Explanation:
# There are no people who are not "it" to catch.
#
# Example 3:
#
# Input: team = [0], dist = 1
# Output: 0
# Explanation:
# There are no people who are "it" to catch people.
#
# Constraints:
#
# 1 <= team.length <= 10^5
#
# 0 <= team[i] <= 1
#
# 1 <= dist <= team.length
#
# @lc code=start
from typing import List


class Solution:
    def catchMaximumAmountofPeople(self, team: List[int], dist: int) -> int:
        """
        Interview explanation:
        Premium. team[i]=1 is "it", 0 is not. Each it can catch at most one
        non-it within index distance dist; each person caught once. Maximize
        catches via two pointers / greedy.

        Algorithm:
        - Collect indices of 0s and 1s; two-pointer: for each catcher, take the
          earliest uncaught person in [i-dist, i+dist].

        Complexity: O(n) time, O(n) space.
        """
        zeros = [i for i, x in enumerate(team) if x == 0]
        ones = [i for i, x in enumerate(team) if x == 1]
        ans = 0
        j = 0
        m = len(zeros)
        for i in ones:
            while j < m and zeros[j] < i - dist:
                j += 1
            if j < m and zeros[j] <= i + dist:
                ans += 1
                j += 1
        return ans

    def catchMaximumAmountofPeople_deque(self, team: List[int], dist: int) -> int:
        """
        Interview explanation:
        Alternate greedy with a queue of available non-it people ahead/behind.

        Algorithm:
        - Scan left to right; maintain queue of unmatched 0 indices; match 1s.

        Complexity: O(n) time, O(n) space.
        """
        from collections import deque

        q = deque()
        ans = 0
        # First pass gather; use same two-list approach for clarity equivalent
        zeros = deque(i for i, x in enumerate(team) if x == 0)
        for i, x in enumerate(team):
            if x != 1:
                continue
            while zeros and zeros[0] < i - dist:
                zeros.popleft()
            if zeros and zeros[0] <= i + dist:
                zeros.popleft()
                ans += 1
        return ans
# @lc code=end

