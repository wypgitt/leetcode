#
# @lc app=leetcode id=3135 lang=python3
#
# [3135] Equalize Strings by Adding or Removing Characters at Ends
#
# https://leetcode.com/problems/equalize-strings-by-adding-or-removing-characters-at-ends/description/
#
# algorithms
# Medium (56.65%)
# Likes:    16
# Dislikes: 2
# Total Accepted:    1.5K
# Total Submissions: 2.7K
# Testcase Example:  "\"abcde\"\n\"cdef\""
#
#
# Given two strings initial and target, your task is to modify initial by
# performing a series of operations to make it equal to target.
#
# In one operation, you can add or remove one character only at the
# beginning or the end of the string initial.
#
# Return the minimum number of operations required to transform initial
# into target.
#
# Example 1:
#
# Input: initial = "abcde", target = "cdef"
#
# Output: 3
#
# Explanation:
#
# Remove 'a' and 'b' from the beginning of initial, then add 'f' to the
# end.
#
# Example 2:
#
# Input: initial = "axxy", target = "yabx"
#
# Output: 6
#
# Explanation:
#
#                         Operation
#                         Resulting String
#
#                         Add 'y' to the beginning
#                         "yaxxy"
#
#                         Remove from end
#                         "yaxx"
#
#                         Remove from end
#                         "yax"
#
#                         Remove from end
#                         "ya"
#
#                         Add 'b' to the end
#                         "yab"
#
#                         Add 'x' to the end
#                         "yabx"
#
# Example 3:
#
# Input: initial = "xyz", target = "xyz"
#
# Output: 0
#
# Explanation:
#
# No operations are needed as the strings are already equal.
#
# Constraints:
#
# 1 <= initial.length, target.length <= 1000
#
# initial and target consist only of lowercase English letters.
#

# @lc code=start
class Solution:
    def minOperations(self, initial: str, target: str) -> int:
        """
        Interview explanation:
        Only add/remove characters at the ends of `initial`. The surviving
        middle must be a contiguous substring of both strings; minimize
        removals+additions to turn initial into target.

        Algorithm:
        - Find longest common substring length L (DP).
        - Answer = len(initial) + len(target) - 2*L.

        Complexity: O(|initial|*|target|) time and space.
        """
        m, n = len(initial), len(target)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        best = 0
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if initial[i - 1] == target[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    if dp[i][j] > best:
                        best = dp[i][j]
        return m + n - 2 * best
# @lc code=end
