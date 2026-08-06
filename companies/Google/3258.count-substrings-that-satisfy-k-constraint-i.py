#
# @lc app=leetcode id=3258 lang=python3
#
# [3258] Count Substrings That Satisfy K-Constraint I
#
# https://leetcode.com/problems/count-substrings-that-satisfy-k-constraint-i/description/
#
# algorithms
# Easy (79.33%)
# Likes:    193
# Dislikes: 38
# Total Accepted:    61.3K
# Total Submissions: 77.3K
# Testcase Example:  "\"10101\"\n1"
#
#
# You are given a binary string s and an integer k.
#
# A binary string satisfies the k-constraint if either of the following
# conditions holds:
#
# The number of 0's in the string is at most k.
#
# The number of 1's in the string is at most k.
#
# Return an integer denoting the number of substrings of s that satisfy
# the k-constraint.
#
# Example 1:
#
# Input: s = "10101", k = 1
#
# Output: 12
#
# Explanation:
#
# Every substring of s except the substrings "1010", "10101", and "0101"
# satisfies the k-constraint.
#
# Example 2:
#
# Input: s = "1010101", k = 2
#
# Output: 25
#
# Explanation:
#
# Every substring of s except the substrings with a length greater than 5
# satisfies the k-constraint.
#
# Example 3:
#
# Input: s = "11111", k = 1
#
# Output: 15
#
# Explanation:
#
# All substrings of s satisfy the k-constraint.
#
# Constraints:
#
# 1 <= s.length <= 50
#
# 1 <= k <= s.length
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def countKConstraintSubstrings(self, s: str, k: int) -> int:
        """
        Interview explanation:
        A substring is valid if zeros <= k or ones <= k (equivalently: not both
        counts exceed k). Sliding window counts all valid substrings.

        Algorithm:
        - Expand right; while zeros > k and ones > k, advance left.
        - Every window [left, right] contributes (right-left+1) valid ends.

        Complexity: O(n) time, O(1) space. n <= 50 also allows O(n^2).
        """
        ans = left = zeros = ones = 0
        for right, ch in enumerate(s):
            if ch == "0":
                zeros += 1
            else:
                ones += 1
            while zeros > k and ones > k:
                if s[left] == "0":
                    zeros -= 1
                else:
                    ones -= 1
                left += 1
            ans += right - left + 1
        return ans
# @lc code=end
