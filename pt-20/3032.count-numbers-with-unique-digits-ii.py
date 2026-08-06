#
# @lc app=leetcode id=3032 lang=python3
#
# [3032] Count Numbers With Unique Digits II
#
# https://leetcode.com/problems/count-numbers-with-unique-digits-ii/description/
#
# algorithms
# Easy (87.31%)
# Likes:    37
# Dislikes: 4
# Total Accepted:    8.8K
# Total Submissions: 10.1K
# Testcase Example:  "1\n20"
#
#
# Given two positive integers a and b, return the count of numbers having
# unique digits in the range [a, b] (inclusive).
#
# Example 1:
#
# Input: a = 1, b = 20
# Output: 19
# Explanation: All the numbers in the range [1, 20] have unique digits
# except 11. Hence, the answer is 19.
#
# Example 2:
#
# Input: a = 9, b = 19
# Output: 10
# Explanation: All the numbers in the range [9, 19] have unique digits
# except 11. Hence, the answer is 10.
#
# Example 3:
#
# Input: a = 80, b = 120
# Output: 27
# Explanation: There are 41 numbers in the range [80, 120], 27 of which
# have unique digits.
#
# Constraints:
#
# 1 <= a <= b <= 1000
#

# @lc code=start

class Solution:
    def numberCount(self, a: int, b: int) -> int:
        """
        Interview explanation:
        Count integers in [a,b] whose decimal digits are all distinct.
        Bounds are tiny (b<=1000), so a direct scan is fine.

        Algorithm:
        - For each x in [a,b], check len(set(str(x))) == len(str(x)).

        Complexity: O((b-a)*D) time with D<=4, O(1) space.
        """
        return sum(len(set(str(x))) == len(str(x)) for x in range(a, b + 1))
# @lc code=end
