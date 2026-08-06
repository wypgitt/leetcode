#
# @lc app=leetcode id=3044 lang=python3
#
# [3044] Most Frequent Prime
#
# https://leetcode.com/problems/most-frequent-prime/description/
#
# algorithms
# Medium (46.32%)
# Likes:    105
# Dislikes: 70
# Total Accepted:    19.6K
# Total Submissions: 42.2K
# Testcase Example:  "[[1,1],[9,9],[1,1]]"
#
#
# You are given a m x n 0-indexed 2D matrix mat. From every cell, you can
# create numbers in the following way:
#
# There could be at most 8 paths from the cells namely: east, south-east,
# south, south-west, west, north-west, north, and north-east.
#
# Select a path from them and append digits in this path to the number
# being formed by traveling in this direction.
#
# Note that numbers are generated at every step, for example, if the
# digits along the path are 1, 9, 1, then there will be three numbers
# generated along the way: 1, 19, 191.
#
# Return the most frequent prime number greater than 10 out of all the
# numbers created by traversing the matrix or -1 if no such prime number
# exists. If there are multiple prime numbers with the highest frequency,
# then return the largest among them.
#
# Note: It is invalid to change the direction during the move.
#
# Example 1:
#
# Input: mat = [[1,1],[9,9],[1,1]]
# Output: 19
# Explanation:
# From cell (0,0) there are 3 possible directions and the numbers greater
# than 10 which can be created in those directions are:
# East: [11], South-East: [19], South: [19,191].
# Numbers greater than 10 created from the cell (0,1) in all possible
# directions are: [19,191,19,11].
# Numbers greater than 10 created from the cell (1,0) in all possible
# directions are: [99,91,91,91,91].
# Numbers greater than 10 created from the cell (1,1) in all possible
# directions are: [91,91,99,91,91].
# Numbers greater than 10 created from the cell (2,0) in all possible
# directions are: [11,19,191,19].
# Numbers greater than 10 created from the cell (2,1) in all possible
# directions are: [11,19,19,191].
# The most frequent prime number among all the created numbers is 19.
#
# Example 2:
#
# Input: mat = [[7]]
# Output: -1
# Explanation: The only number which can be formed is 7. It is a prime
# number however it is not greater than 10, so return -1.
#
# Example 3:
#
# Input: mat = [[9,7,8],[4,6,5],[2,8,6]]
# Output: 97
# Explanation:
# Numbers greater than 10 created from the cell (0,0) in all possible
# directions are: [97,978,96,966,94,942].
# Numbers greater than 10 created from the cell (0,1) in all possible
# directions are: [78,75,76,768,74,79].
# Numbers greater than 10 created from the cell (0,2) in all possible
# directions are: [85,856,86,862,87,879].
# Numbers greater than 10 created from the cell (1,0) in all possible
# directions are: [46,465,48,42,49,47].
# Numbers greater than 10 created from the cell (1,1) in all possible
# directions are: [65,66,68,62,64,69,67,68].
# Numbers greater than 10 created from the cell (1,2) in all possible
# directions are: [56,58,56,564,57,58].
# Numbers greater than 10 created from the cell (2,0) in all possible
# directions are: [28,286,24,249,26,268].
# Numbers greater than 10 created from the cell (2,1) in all possible
# directions are: [86,82,84,86,867,85].
# Numbers greater than 10 created from the cell (2,2) in all possible
# directions are: [68,682,66,669,65,658].
# The most frequent prime number among all the created numbers is 97.
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 6
#
# 1 <= mat[i][j] <= 9
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def mostFrequentPrime(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        From every cell, walk each of 8 straight directions, forming numbers
        digit-by-digit. Among primes > 10, return the most frequent (ties: max).

        Algorithm:
        - Enumerate all rays; trial-division primality; Counter; pick by (freq, value).

        Complexity: O(m*n*max(m,n)*sqrt(V)) time with V up to ~10^digits, grid <= 6x6.
        """
        m, n = len(mat), len(mat[0])
        dirs = (
            (0, 1), (1, 1), (1, 0), (1, -1),
            (0, -1), (-1, -1), (-1, 0), (-1, 1),
        )
        freq: Counter[int] = Counter()

        def is_prime(x: int) -> bool:
            if x < 2:
                return False
            if x % 2 == 0:
                return x == 2
            d = 3
            while d * d <= x:
                if x % d == 0:
                    return False
                d += 2
            return True

        for i in range(m):
            for j in range(n):
                for di, dj in dirs:
                    x, y, val = i, j, 0
                    while 0 <= x < m and 0 <= y < n:
                        val = val * 10 + mat[x][y]
                        if val > 10 and is_prime(val):
                            freq[val] += 1
                        x += di
                        y += dj
        if not freq:
            return -1
        best_c = max(freq.values())
        return max(p for p, c in freq.items() if c == best_c)
# @lc code=end

