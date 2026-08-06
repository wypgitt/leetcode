#
# @lc app=leetcode id=1051 lang=python3
#
# [1051] Height Checker
#
# https://leetcode.com/problems/height-checker/description/
#
# algorithms
# Easy (81.9%)
# Likes:    1827
# Dislikes: 124
# Total Accepted:    662K
# Total Submissions: 808K
# Testcase Example:  "[1,1,4,2,1,3]"
#
# A school is trying to take an annual photo of all the students. The students
# are asked to stand in a single file line in non-decreasing order by height.
# Let this ordering be represented by the integer array expected where
# expected[i] is the expected height of the i^th student in line.
#
# You are given an integer array heights representing the current order that
# the students are standing in. Each heights[i] is the height of the i^th
# student in line (0-indexed).
#
# Return the number of indices where heights[i] != expected[i].
#
# Example 1:
#
# Input: heights = [1,1,4,2,1,3]
# Output: 3
# Explanation:
# heights: [1,1,4,2,1,3]
# expected: [1,1,1,2,3,4]
# Indices 2, 4, and 5 do not match.
#
# Example 2:
#
# Input: heights = [5,1,2,3,4]
# Output: 5
# Explanation:
# heights: [5,1,2,3,4]
# expected: [1,2,3,4,5]
# All indices do not match.
#
# Example 3:
#
# Input: heights = [1,2,3,4,5]
# Output: 0
# Explanation:
# heights: [1,2,3,4,5]
# expected: [1,2,3,4,5]
# All indices match.
#
# Constraints:
#
# 1 <= heights.length <= 100
#
# 1 <= heights[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def heightChecker(self, heights: List[int]) -> int:
        """
        Interview explanation:
        Expected non-decreasing order is sorted(heights). Count indices where
        heights[i] != expected[i].

        Algorithm:
        - expected = sorted(heights); sum(h!=e)

        Complexity: O(n log n) time, O(n) space.
        """
        expected = sorted(heights)
        return sum(h != e for h, e in zip(heights, expected))

    def heightChecker_counting(self, heights: List[int]) -> int:
        """
        Interview explanation:
        Alternate counting sort since heights in [1,100]: build frequency then
        walk expected order comparing.

        Algorithm:
        - Count freq[1..100]; walk heights vs reconstructed sorted sequence

        Complexity: O(n + M) time, O(M) space with M=100.
        """
        freq = [0] * 101
        for h in heights:
            freq[h] += 1
        ans = i = 0
        for h in range(1, 101):
            for _ in range(freq[h]):
                if heights[i] != h:
                    ans += 1
                i += 1
        return ans
# @lc code=end
