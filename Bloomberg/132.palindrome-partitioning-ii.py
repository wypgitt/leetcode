#
# @lc app=leetcode id=132 lang=python3
#
# [132] Palindrome Partitioning II
#
# https://leetcode.com/problems/palindrome-partitioning-ii/description/
#
# algorithms
# Hard (37.66%)
# Likes:    6014
# Dislikes: 160
# Total Accepted:    437K
# Total Submissions: 1.2M
# Testcase Example:  "\"aab\""
#
# Given a string s, partition s such that every substring of the partition is a
# palindrome.
#
# Return the minimum cuts needed for a palindrome partitioning of s.
#
# Example 1:
#
# Input: s = "aab"
# Output: 1
# Explanation: The palindrome partitioning ["aa","b"] could be produced using 1
# cut.
#
# Example 2:
#
# Input: s = "a"
# Output: 0
#
# Example 3:
#
# Input: s = "ab"
# Output: 1
#
# Constraints:
#
# 1 <= s.length <= 2000
#
# s consists of lowercase English letters only.
#

# @lc code=start
class Solution:
    def minCut(self, s: str) -> int:
        """
        Interview explanation:
        Expand every palindromic substring and use it to update the minimum
        cuts needed to partition the prefix ending at that substring's right
        endpoint.

        Algorithm:
        - cut[i] = min cuts for s[:i+1], init cut[i] = i.
        - For each center, expand odd- and even-length palindromes [lo, hi].
        - When s[lo..hi] is palindrome: cut[hi] = 0 if lo == 0 else
          min(cut[hi], cut[lo-1] + 1).

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(s)
        cut = list(range(n))
        for center in range(n):
            for lo, hi in ((center, center), (center, center + 1)):
                while lo >= 0 and hi < n and s[lo] == s[hi]:
                    cut[hi] = 0 if lo == 0 else min(cut[hi], cut[lo - 1] + 1)
                    lo -= 1
                    hi += 1
        return cut[-1]
# @lc code=end
