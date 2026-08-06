#
# @lc app=leetcode id=2472 lang=python3
#
# [2472] Maximum Number of Non-overlapping Palindrome Substrings
#
# https://leetcode.com/problems/maximum-number-of-non-overlapping-palindrome-substrings/description/
#
# algorithms
# Hard (44.97%)
# Likes:    519
# Dislikes: 11
# Total Accepted:    27.3K
# Total Submissions: 60.7K
# Testcase Example:  "\"abaccdbbd\"\n3"
#
# You are given a string s and a positive integer k.
#
# Select a set of non-overlapping substrings from the string s that satisfy the
# following conditions:
#
#
# The length of each substring is at least k.
#
#
# Each substring is a palindrome.
#
# Return the maximum number of substrings in an optimal selection.
#
# A substring is a contiguous sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "abaccdbbd", k = 3
# Output: 2
# Explanation: We can select the substrings underlined in s = "abaccdbbd". Both
# "aba" and "dbbd" are palindromes and have a length of at least k = 3.
# It can be shown that we cannot find a selection with more than two valid
# substrings.
#
# Example 2:
#
# Input: s = "adbcda", k = 2
# Output: 0
# Explanation: There is no palindrome substring of length at least 2 in the
# string.
#
#
#
# Constraints:
#
#
# 1 <= k <= s.length <= 2000
#
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def maxPalindromes(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Max number of non-overlapping palindromic substrings of length >= k.

        Algorithm:
        - Greedy: repeatedly take the leftmost shortest palindrome of length
          k or k+1 (centers), which is optimal for packing.

        Complexity: O(n * k) time, O(1) space.
        """
        n = len(s)
        ans = i = 0

        def is_pal(l: int, r: int) -> bool:
            while l < r:
                if s[l] != s[r]:
                    return False
                l += 1
                r -= 1
            return True

        while i + k <= n:
            # try length k then k+1 starting at i
            if is_pal(i, i + k - 1):
                ans += 1
                i += k
            elif i + k + 1 <= n and is_pal(i, i + k):
                ans += 1
                i += k + 1
            else:
                i += 1
        return ans
# @lc code=end

