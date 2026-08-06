#
# @lc app=leetcode id=2019 lang=python3
#
# [2019] The Score of Students Solving Math Expression
#
# https://leetcode.com/problems/the-score-of-students-solving-math-expression/description/
#
# algorithms
# Hard (34.40%)
# Likes:    283
# Dislikes: 85
# Total Accepted:    9.8K
# Total Submissions: 28.5K
# Testcase Example:  "\"7+3*1*2\"\n[20,13,42]"
#
# You are given a string s that contains digits 0-9, addition symbols '+', and
# multiplication symbols '*' only, representing a valid math expression of
# single digit numbers (e.g., 3+5*2). This expression was given to n elementary
# school students. The students were instructed to get the answer of the
# expression by following this order of operations:
#
#
# Compute multiplication, reading from left to right; Then,
#
#
# Compute addition, reading from left to right.
#
# You are given an integer array answers of length n, which are the submitted
# answers of the students in no particular order. You are asked to grade the
# answers, by following these rules:
#
#
# If an answer equals the correct answer of the expression, this student will be
# rewarded 5 points;
#
#
# Otherwise, if the answer could be interpreted as if the student applied the
# operators in the wrong order but had correct arithmetic, this student will be
# rewarded 2 points;
#
#
# Otherwise, this student will be rewarded 0 points.
#
# Return the sum of the points of the students.
#
#
#
# Example 1:
#
# Input: s = "7+3*1*2", answers = [20,13,42]
# Output: 7
# Explanation: As illustrated above, the correct answer of the expression is 13,
# therefore one student is rewarded 5 points: [20,13,42]
# A student might have applied the operators in this wrong order: ((7+3)*1)*2 =
# 20. Therefore one student is rewarded 2 points: [20,13,42]
# The points for the students are: [2,5,0]. The sum of the points is 2+5+0=7.
#
# Example 2:
#
# Input: s = "3+5*2", answers = [13,0,10,13,13,16,16]
# Output: 19
# Explanation: The correct answer of the expression is 13, therefore three
# students are rewarded 5 points each: [13,0,10,13,13,16,16]
# A student might have applied the operators in this wrong order: ((3+5)*2 = 16.
# Therefore two students are rewarded 2 points: [13,0,10,13,13,16,16]
# The points for the students are: [5,0,0,5,5,2,2]. The sum of the points is
# 5+0+0+5+5+2+2=19.
#
# Example 3:
#
# Input: s = "6+0*1", answers = [12,9,6,4,8,6]
# Output: 10
# Explanation: The correct answer of the expression is 6.
# If a student had incorrectly done (6+0)*1, the answer would also be 6.
# By the rules of grading, the students will still be rewarded 5 points (as they
# got the correct answer), not 2 points.
# The points for the students are: [0,0,5,0,0,5]. The sum of the points is 10.
#
#
#
# Constraints:
#
#
# 3 <= s.length <= 31
#
#
# s represents a valid expression that contains only digits 0-9, '+', and '*'
# only.
#
#
# All the integer operands in the expression are in the inclusive range [0, 9].
#
#
# 1 <= The count of all operators ('+' and '*') in the math expression <= 15
#
#
# Test data are generated such that the correct answer of the expression is in
# the range of [0, 1000].
#
#
# Test data are generated such that value never exceeds 10^9 in intermediate
# steps of multiplication.
#
#
# n == answers.length
#
#
# 1 <= n <= 10^4
#
#
# 0 <= answers[i] <= 1000
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def scoreOfStudents(self, s: str, answers: List[int]) -> int:
        """
        Interview explanation:
        Expression digits with +/*; correct (* before +) scores 5; any value
        from different parenthesizations scores 2; else 0.

        Algorithm:
        - DP all values per substring (cap 1000). Eval correct with * then +.
        - Score each answer.

        Complexity: O(n^3 * V^2) time with V<=1000; O(n^2 V) space.
        """
        nums = [int(s[i]) for i in range(0, len(s), 2)]
        ops = [s[i] for i in range(1, len(s), 2)]
        n = len(nums)

        @lru_cache(None)
        def dfs(l: int, r: int):
            if l == r:
                return frozenset([nums[l]])
            res = set()
            for i in range(l, r):
                for a in dfs(l, i):
                    for b in dfs(i + 1, r):
                        v = a + b if ops[i] == '+' else a * b
                        if v <= 1000:
                            res.add(v)
            return frozenset(res)

        possible = dfs(0, n - 1)

        def correct() -> int:
            vals = nums[:]
            op = ops[:]
            i = 0
            while i < len(op):
                if op[i] == '*':
                    vals[i] = vals[i] * vals[i + 1]
                    del vals[i + 1]
                    del op[i]
                else:
                    i += 1
            ans = vals[0]
            for x in vals[1:]:
                ans += x
            return ans

        right = correct()
        score = 0
        for a in answers:
            if a == right:
                score += 5
            elif a in possible:
                score += 2
        return score
# @lc code=end
