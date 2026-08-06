#
# @lc app=leetcode id=3144 lang=python3
#
# [3144] Minimum Substring Partition of Equal Character Frequency
#
# https://leetcode.com/problems/minimum-substring-partition-of-equal-character-frequency/description/
#
# algorithms
# Medium (40.70%)
# Likes:    182
# Dislikes: 36
# Total Accepted:    19.2K
# Total Submissions: 47.2K
# Testcase Example:  "\"fabccddg\""
#
#
# Given a string s, you need to partition it into one or more balanced
# substrings. For example, if s == "ababcc" then ("abab", "c", "c"),
# ("ab", "abc", "c"), and ("ababcc") are all valid partitions, but ("a",
# "bab", "cc"), ("aba", "bc", "c"), and ("ab", "abcc") are not. The
# unbalanced substrings are bolded.
#
# Return the minimum number of substrings that you can partition s into.
#
# Note: A balanced string is a string where each character in the string
# occurs the same number of times.
#
# Example 1:
#
# Input: s = "fabccddg"
#
# Output: 3
#
# Explanation:
#
# We can partition the string s into 3 substrings in one of the following
# ways: ("fab, "ccdd", "g"), or ("fabc", "cd", "dg").
#
# Example 2:
#
# Input: s = "abababaccddb"
#
# Output: 2
#
# Explanation:
#
# We can partition the string s into 2 substrings like so: ("abab",
# "abaccddb").
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists only of English lowercase letters.
#

# @lc code=start
class Solution:
    def minimumSubstringsInPartition(self, s: str) -> int:
        """
        Interview explanation:
        Partition s into the fewest balanced pieces (every present char has the
        same frequency inside a piece).

        Algorithm:
        - dp[i] = min pieces for s[:i].
        - For each end i, expand start j leftward with a frequency map; when the
          nonzero frequencies are all equal, take dp[j] + 1.

        Complexity: O(n^2 * Σ) time with Σ=26, O(n) space.
        """
        n = len(s)
        INF = 10**9
        dp = [INF] * (n + 1)
        dp[0] = 0
        for i in range(1, n + 1):
            freq = [0] * 26
            for j in range(i - 1, -1, -1):
                freq[ord(s[j]) - 97] += 1
                vals = [f for f in freq if f]
                if len(set(vals)) == 1:
                    dp[i] = min(dp[i], dp[j] + 1)
        return dp[n]
# @lc code=end
