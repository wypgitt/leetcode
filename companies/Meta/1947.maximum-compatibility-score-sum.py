#
# @lc app=leetcode id=1947 lang=python3
#
# [1947] Maximum Compatibility Score Sum
#
# https://leetcode.com/problems/maximum-compatibility-score-sum/description/
#
# algorithms
# Medium (64.78%)
# Likes:    839
# Dislikes: 32
# Total Accepted:    35.4K
# Total Submissions: 54.7K
# Testcase Example:  "[[1,1,0],[1,0,1],[0,0,1]]"
#
# There is a survey that consists of n questions where each question's answer
# is either 0 (no) or 1 (yes).
#
# The survey was given to m students numbered from 0 to m - 1 and m mentors
# numbered from 0 to m - 1. The answers of the students are represented by a 2D
# integer array students where students[i] is an integer array that contains
# the answers of the i^th student (0-indexed). The answers of the mentors are
# represented by a 2D integer array mentors where mentors[j] is an integer
# array that contains the answers of the j^th mentor (0-indexed).
#
# Each student will be assigned to one mentor, and each mentor will have one
# student assigned to them. The compatibility score of a student-mentor pair is
# the number of answers that are the same for both the student and the mentor.
#
# For example, if the student's answers were [1, 0, 1] and the mentor's answers
# were [0, 0, 1], then their compatibility score is 2 because only the second
# and the third answers are the same.
#
# You are tasked with finding the optimal student-mentor pairings to maximize
# the sum of the compatibility scores.
#
# Given students and mentors, return the maximum compatibility score sum that
# can be achieved.
#
# Example 1:
#
# Input: students = [[1,1,0],[1,0,1],[0,0,1]], mentors =
# [[1,0,0],[0,0,1],[1,1,0]]
# Output: 8
# Explanation: We assign students to mentors in the following way:
# - student 0 to mentor 2 with a compatibility score of 3.
# - student 1 to mentor 0 with a compatibility score of 2.
# - student 2 to mentor 1 with a compatibility score of 3.
# The compatibility score sum is 3 + 2 + 3 = 8.
#
# Example 2:
#
# Input: students = [[0,0],[0,0],[0,0]], mentors = [[1,1],[1,1],[1,1]]
# Output: 0
# Explanation: The compatibility score of any student-mentor pair is 0.
#
# Constraints:
#
# m == students.length == mentors.length
#
# n == students[i].length == mentors[j].length
#
# 1 <= m, n <= 8
#
# students[i][k] is either 0 or 1.
#
# mentors[j][k] is either 0 or 1.
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def maxCompatibilitySum(self, students: List[List[int]], mentors: List[List[int]]) -> int:
        """
        Interview explanation:
        Assign each student to a distinct mentor to max sum of answer agreements.
        m≤8 → bitmask DP / backtracking over mentor subset.

        Algorithm:
        - score[i][j] = agreements. DP[mask] = max score assigning next student
          to a free mentor in mask (or iterate students by popcount).

        Complexity: O(m^2 * 2^m + m^2 * n) time.
        """
        m = len(students)
        score = [[0] * m for _ in range(m)]
        for i in range(m):
            for j in range(m):
                score[i][j] = sum(a == b for a, b in zip(students[i], mentors[j]))

        @lru_cache(None)
        def dp(i: int, mask: int) -> int:
            if i == m:
                return 0
            best = 0
            for j in range(m):
                if not (mask & (1 << j)):
                    best = max(best, score[i][j] + dp(i + 1, mask | (1 << j)))
            return best

        return dp(0, 0)

    def maxCompatibilitySum_backtrack(self, students: List[List[int]], mentors: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate: plain backtracking permutation of mentors.

        Algorithm:
        - Try unused mentors for student i; track global max.

        Complexity: O(m!) with pruning optional.
        """
        m = len(students)
        score = [[sum(a == b for a, b in zip(students[i], mentors[j])) for j in range(m)] for i in range(m)]
        used = [False] * m
        self.ans = 0

        def bt(i: int, cur: int):
            if i == m:
                self.ans = max(self.ans, cur)
                return
            for j in range(m):
                if not used[j]:
                    used[j] = True
                    bt(i + 1, cur + score[i][j])
                    used[j] = False

        bt(0, 0)
        return self.ans
# @lc code=end
