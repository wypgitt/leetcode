#
# @lc app=leetcode id=3337 lang=python3
#
# [3337] Total Characters in String After Transformations II
#
# https://leetcode.com/problems/total-characters-in-string-after-transformations-ii/description/
#
# algorithms
# Hard (57.64%)
# Likes:    392
# Dislikes: 83
# Total Accepted:    63.9K
# Total Submissions: 110.8K
# Testcase Example:  "\"abcyy\"\n2\n[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2]"
#
#
# You are given a string s consisting of lowercase English letters, an
# integer t representing the number of transformations to perform, and an
# array nums of size 26. In one transformation, every character in s is
# replaced according to the following rules:
#
# Replace s[i] with the next nums[s[i] - 'a'] consecutive characters in
# the alphabet. For example, if s[i] = 'a' and nums[0] = 3, the character
# 'a' transforms into the next 3 consecutive characters ahead of it, which
# results in "bcd".
#
# The transformation wraps around the alphabet if it exceeds 'z'. For
# example, if s[i] = 'y' and nums[24] = 3, the character 'y' transforms
# into the next 3 consecutive characters ahead of it, which results in
# "zab".
#
# Return the length of the resulting string after exactly t
# transformations.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "abcyy", t = 2, nums =
# [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2]
#
# Output: 7
#
# Explanation:
#
# First Transformation (t = 1):
#
# 'a' becomes 'b' as nums[0] == 1
#
# 'b' becomes 'c' as nums[1] == 1
#
# 'c' becomes 'd' as nums[2] == 1
#
# 'y' becomes 'z' as nums[24] == 1
#
# 'y' becomes 'z' as nums[24] == 1
#
# String after the first transformation: "bcdzz"
#
# Second Transformation (t = 2):
#
# 'b' becomes 'c' as nums[1] == 1
#
# 'c' becomes 'd' as nums[2] == 1
#
# 'd' becomes 'e' as nums[3] == 1
#
# 'z' becomes 'ab' as nums[25] == 2
#
# 'z' becomes 'ab' as nums[25] == 2
#
# String after the second transformation: "cdeabab"
#
# Final Length of the string: The string is "cdeabab", which has 7
# characters.
#
# Example 2:
#
# Input: s = "azbk", t = 1, nums =
# [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
#
# Output: 8
#
# Explanation:
#
# First Transformation (t = 1):
#
# 'a' becomes 'bc' as nums[0] == 2
#
# 'z' becomes 'ab' as nums[25] == 2
#
# 'b' becomes 'cd' as nums[1] == 2
#
# 'k' becomes 'lm' as nums[10] == 2
#
# String after the first transformation: "bcabcdlm"
#
# Final Length of the string: The string is "bcabcdlm", which has 8
# characters.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#
# 1 <= t <= 10^9
#
# nums.length == 26
#
# 1 <= nums[i] <= 25
#

# @lc code=start

from typing import List


class Solution:
    def lengthAfterTransformations(self, s: str, t: int, nums: List[int]) -> int:
        """
        Interview explanation:
        Generalization of I: letter i expands into the next nums[i] letters
        (wrap). t can be 1e9 → matrix exponentiation on the 26×26 transition.

        Algorithm:
        - Build T where T[i][(i+step)%26] += 1 for step in 1..nums[i].
        - lengths = count * T^t; answer = sum(lengths) mod 1e9+7.

        Complexity: O(26^3 log t + |s|) time, O(26^2) space.
        """
        MOD = 10**9 + 7

        def mat_mul(a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
            n = len(a)
            c = [[0] * n for _ in range(n)]
            for i in range(n):
                for k in range(n):
                    if a[i][k] == 0:
                        continue
                    aik = a[i][k]
                    for j in range(n):
                        c[i][j] = (c[i][j] + aik * b[k][j]) % MOD
            return c

        def mat_pow(mat: List[List[int]], e: int) -> List[List[int]]:
            n = len(mat)
            res = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
            while e:
                if e & 1:
                    res = mat_mul(res, mat)
                mat = mat_mul(mat, mat)
                e >>= 1
            return res

        T = [[0] * 26 for _ in range(26)]
        for i, steps in enumerate(nums):
            for step in range(1, steps + 1):
                T[i][(i + step) % 26] += 1

        P = mat_pow(T, t)
        count = [0] * 26
        for ch in s:
            count[ord(ch) - 97] += 1

        ans = 0
        for i in range(26):
            for j in range(26):
                ans = (ans + count[i] * P[i][j]) % MOD
        return ans
# @lc code=end

