#
# @lc app=leetcode id=2730 lang=python3
#
# [2730] Find the Longest Semi-Repetitive Substring
#
# https://leetcode.com/problems/find-the-longest-semi-repetitive-substring/description/
#
# algorithms
# Medium (39.28%)
# Likes:    320
# Dislikes: 89
# Total Accepted:    34.6K
# Total Submissions: 88K
# Testcase Example:  "\"52233\""
#
# You are given a digit string s that consists of digits from 0 to 9.
#
# A string is called semi-repetitive if there is at most one adjacent pair of
# the same digit. For example, "0010", "002020", "0123", "2002", and "54944" are
# semi-repetitive while the following are not: "00101022" (adjacent same digit
# pairs are 00 and 22), and "1101234883" (adjacent same digit pairs are 11 and
# 88).
#
# Return the length of the longest semi-repetitive substring of s.
#
#
#
# Example 1:
#
# Input: s = "52233"
#
# Output: 4
#
# Explanation:
#
# The longest semi-repetitive substring is "5223". Picking the whole string
# "52233" has two adjacent same digit pairs 22 and 33, but at most one is
# allowed.
#
# Example 2:
#
# Input: s = "5494"
#
# Output: 4
#
# Explanation:
#
# s is a semi-repetitive string.
#
# Example 3:
#
# Input: s = "1111111"
#
# Output: 2
#
# Explanation:
#
# The longest semi-repetitive substring is "11". Picking the substring "111" has
# two adjacent same digit pairs, but at most one is allowed.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 50
#
#
# '0' <= s[i] <= '9'
#

# @lc code=start
class Solution:
    def longestSemiRepetitiveSubstring(self, s: str) -> int:
        """
        Interview explanation:
        Longest substring with at most one adjacent equal pair (semi-repetitive).

        Algorithm:
        - Sliding window; track count of adjacent equal pairs inside; shrink when > 1.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        ans = 1
        left = 0
        pairs = 0
        for right in range(1, n):
            if s[right] == s[right - 1]:
                pairs += 1
            while pairs > 1:
                if s[left + 1] == s[left]:
                    pairs -= 1
                left += 1
            ans = max(ans, right - left + 1)
        return ans

    def longestSemiRepetitiveSubstring_two_pointers(self, s: str) -> int:
        """
        Interview explanation:
        Alternate naming for the sliding-window approach.

        Algorithm:
        - Same two pointers with pair counter.

        Complexity: O(n) time, O(1) space.
        """
        return self.longestSemiRepetitiveSubstring(s)
# @lc code=end
