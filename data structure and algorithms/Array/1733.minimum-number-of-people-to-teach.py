#
# @lc app=leetcode id=1733 lang=python3
#
# [1733] Minimum Number of People to Teach
#
# https://leetcode.com/problems/minimum-number-of-people-to-teach/description/
#
# algorithms
# Medium (67.25%)
# Likes:    716
# Dislikes: 560
# Total Accepted:    101K
# Total Submissions: 150K
# Testcase Example:  "2"
#
# On a social network consisting of m users and some friendships between users,
# two users can communicate with each other if they know a common language.
#
# You are given an integer n, an array languages, and an array friendships
# where:
#
# There are n languages numbered 1 through n,
#
# languages[i] is the set of languages the i^th user knows, and
#
# friendships[i] = [u_i, v_i] denotes a friendship between the users u^_i and
# v_i.
#
# You can choose one language and teach it to some users so that all friends
# can communicate with each other. Return the minimum number of users you need
# to teach.
#
# Note that friendships are not transitive, meaning if x is a friend of y and y
# is a friend of z, this doesn't guarantee that x is a friend of z.
#
# Example 1:
#
# Input: n = 2, languages = [[1],[2],[1,2]], friendships = [[1,2],[1,3],[2,3]]
# Output: 1
# Explanation: You can either teach user 1 the second language or user 2 the
# first language.
#
# Example 2:
#
# Input: n = 3, languages = [[2],[1,3],[1,2],[3]], friendships =
# [[1,4],[1,2],[3,4],[2,3]]
# Output: 2
# Explanation: Teach the third language to users 1 and 3, yielding two users to
# teach.
#
# Constraints:
#
# 2 <= n <= 500
#
# languages.length == m
#
# 1 <= m <= 500
#
# 1 <= languages[i].length <= n
#
# 1 <= languages[i][j] <= n
#
# 1 <= u_i < v_i <= languages.length
#
# 1 <= friendships.length <= 500
#
# All tuples (u_i, v_i) are unique
#
# languages[i] contains only unique values
#

# @lc code=start
from typing import List


class Solution:
    def minimumTeachings(self, n: int, languages: List[List[int]], friendships: List[List[int]]) -> int:
        """
        Interview explanation:
        Teach one language to fewest people so every friendship shares a language.
        Only users in friendships without a shared language matter; pick the
        language minimizing how many of those users need to learn it.

        Algorithm:
        - know[i] = set(languages[i]); collect bad users from non-communicating friendships.
        - For each language 1..n count bad users missing it; return min.

        Complexity: O(m*L + |F|*L + n*|bad|) time.
        """
        know = [set(langs) for langs in languages]
        bad = set()
        for a, b in friendships:
            a -= 1
            b -= 1
            if know[a].isdisjoint(know[b]):
                bad.add(a)
                bad.add(b)
        if not bad:
            return 0
        ans = len(bad)
        for lang in range(1, n + 1):
            need = sum(1 for u in bad if lang not in know[u])
            ans = min(ans, need)
        return ans
# @lc code=end
