#
# @lc app=leetcode id=1663 lang=python3
#
# [1663] Smallest String With A Given Numeric Value
#
# https://leetcode.com/problems/smallest-string-with-a-given-numeric-value/description/
#
# algorithms
# Medium (67.53%)
# Likes:    1927
# Dislikes: 64
# Total Accepted:    107K
# Total Submissions: 158K
# Testcase Example:  "3"
#
# The numeric value of a lowercase character is defined as its position
# (1-indexed) in the alphabet, so the numeric value of a is 1, the numeric
# value of b is 2, the numeric value of c is 3, and so on.
#
# The numeric value of a string consisting of lowercase characters is defined
# as the sum of its characters' numeric values. For example, the numeric value
# of the string "abe" is equal to 1 + 2 + 5 = 8.
#
# You are given two integers n and k. Return the lexicographically smallest
# string with length equal to n and numeric value equal to k.
#
# Note that a string x is lexicographically smaller than string y if x comes
# before y in dictionary order, that is, either x is a prefix of y, or if i is
# the first position such that x[i] != y[i], then x[i] comes before y[i] in
# alphabetic order.
#
# Example 1:
#
# Input: n = 3, k = 27
# Output: "aay"
# Explanation: The numeric value of the string is 1 + 1 + 25 = 27, and it is
# the smallest string with such a value and length equal to 3.
#
# Example 2:
#
# Input: n = 5, k = 73
# Output: "aaszz"
#
# Constraints:
#
# 1 <= n <= 10^5
#
# n <= k <= 26 * n
#

# @lc code=start
class Solution:
    def getSmallestString(self, n: int, k: int) -> str:
        """
        Interview explanation:
        Numeric value a=1..z=26; length n summing to k; lexicographically smallest.
        Greedy: fill from the right with as large as possible (min(26, remaining
        after reserving 1 for each left slot)).

        Algorithm:
        - arr=['a']*n; rem=k-n; from right: add=min(25,rem); arr[i]+=add; rem-=add

        Complexity: O(n) time, O(n) space.
        """
        arr = ["a"] * n
        rem = k - n
        i = n - 1
        while rem > 0:
            add = min(25, rem)
            arr[i] = chr(ord("a") + add)
            rem -= add
            i -= 1
        return "".join(arr)
# @lc code=end
