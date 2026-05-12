#
# @lc app=leetcode id=1208 lang=python3
#
# [1208] Get Equal Substrings Within Budget
#
# https://leetcode.com/problems/get-equal-substrings-within-budget/description/
#
# algorithms
# Medium (59.66%)
# Likes:    1929
# Dislikes: 150
# Total Accepted:    202.6K
# Total Submissions: 339.5K
# Testcase Example:  '"abcd"\n"bcdf"\n3'
#
# You are given two strings s and t of the same length and an integer maxCost.
# 
# You want to change s to t. Changing the i^th character of s to i^th character
# of t costs |s[i] - t[i]| (i.e., the absolute difference between the ASCII
# values of the characters).
# 
# Return the maximum length of a substring of s that can be changed to be the
# same as the corresponding substring of t with a cost less than or equal to
# maxCost. If there is no substring from s that can be changed to its
# corresponding substring from t, return 0.
# 
# 
# Example 1:
# 
# 
# Input: s = "abcd", t = "bcdf", maxCost = 3
# Output: 3
# Explanation: "abc" of s can change to "bcd".
# That costs 3, so the maximum length is 3.
# 
# 
# Example 2:
# 
# 
# Input: s = "abcd", t = "cdef", maxCost = 3
# Output: 1
# Explanation: Each character in s costs 2 to change to character in t,  so the
# maximum length is 1.
# 
# 
# Example 3:
# 
# 
# Input: s = "abcd", t = "acde", maxCost = 0
# Output: 1
# Explanation: You cannot make any change, so the maximum length is 1.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# t.length == s.length
# 0 <= maxCost <= 10^6
# s and t consist of only lowercase English letters.
# 
# 
#

# @lc code=start
class Solution:
    def equalSubstring(self, s: str, t: str, maxCost: int) -> int:
        left = 0
        cost = 0
        best = 0

        for right, (a, b) in enumerate(zip(s, t)):
            cost += abs(ord(a) - ord(b))

            while cost > maxCost:
                cost -= abs(ord(s[left]) - ord(t[left]))
                left += 1

            best = max(best, right - left + 1)

        return best
# @lc code=end

# Explanation
# -----------
# Convert the problem into an array of costs where cost[i] is the price to
# change s[i] into t[i]. We need the longest contiguous subarray whose sum is
# at most maxCost, which is the classic variable-size sliding-window pattern.
# The right pointer expands the window and adds cost. If the budget is
# exceeded, the left pointer shrinks the window until the invariant
# "current window cost <= maxCost" is true again. Every valid window ending at
# right is then considered for the answer.
#
# A sliding window is better than prefix sums plus binary search here because
# all costs are nonnegative, so expanding right can only increase the sum and
# moving left can only decrease it. That monotonic behavior gives one linear
# pass.
#
# Edge cases: maxCost = 0 still works because only zero-cost positions can
# remain in the window; a single character string is handled naturally; if no
# positive-length window is affordable, best remains 0.
#
# Time complexity: O(n), because each pointer moves at most n times.
# Space complexity: O(1).
