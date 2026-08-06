#
# @lc app=leetcode id=2582 lang=python3
#
# [2582] Pass the Pillow
#
# https://leetcode.com/problems/pass-the-pillow/description/
#
# algorithms
# Easy (56.59%)
# Likes:    1111
# Dislikes: 59
# Total Accepted:    219.2K
# Total Submissions: 387.3K
# Testcase Example:  "4\n5"
#
# There are n people standing in a line labeled from 1 to n. The first person in
# the line is holding a pillow initially. Every second, the person holding the
# pillow passes it to the next person standing in the line. Once the pillow
# reaches the end of the line, the direction changes, and people continue
# passing the pillow in the opposite direction.
#
#
# For example, once the pillow reaches the n^th person they pass it to the n -
# 1^th person, then to the n - 2^th person and so on.
#
# Given the two positive integers n and time, return the index of the person
# holding the pillow after time seconds.
#
#
#
# Example 1:
#
# Input: n = 4, time = 5
# Output: 2
# Explanation: People pass the pillow in the following way: 1 -> 2 -> 3 -> 4 ->
# 3 -> 2.
# After five seconds, the 2^nd person is holding the pillow.
#
# Example 2:
#
# Input: n = 3, time = 2
# Output: 3
# Explanation: People pass the pillow in the following way: 1 -> 2 -> 3.
# After two seconds, the 3^r^d person is holding the pillow.
#
#
#
# Constraints:
#
#
# 2 <= n <= 1000
#
#
# 1 <= time <= 1000
#
#
#
# Note: This question is the same as  3178: Find the Child Who Has the Ball
# After K Seconds.
#

# @lc code=start
class Solution:
    def passThePillow(self, n: int, time: int) -> int:
        """
        Interview explanation:
        Pillow passes 1->n then back to 1. Find holder after `time` seconds.

        Algorithm:
        - Period is 2*(n-1). Position in cycle via modulo; map to index.

        Complexity: O(1) time and space.
        """
        cycle = 2 * (n - 1)
        t = time % cycle
        if t < n:
            return 1 + t
        return n - (t - (n - 1))
# @lc code=end
