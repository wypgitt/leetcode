#
# @lc app=leetcode id=2405 lang=python3
#
# [2405] Optimal Partition of String
#
# https://leetcode.com/problems/optimal-partition-of-string/description/
#
# algorithms
# Medium (78.50%)
# Likes:    2824
# Dislikes: 115
# Total Accepted:    282.6K
# Total Submissions: 360.1K
# Testcase Example:  "\"abacaba\""
#
# Given a string s, partition the string into one or more substrings such that
# the characters in each substring are unique. That is, no letter appears in a
# single substring more than once.
#
# Return the minimum number of substrings in such a partition.
#
# Note that each character should belong to exactly one substring in a
# partition.
#
#
#
# Example 1:
#
# Input: s = "abacaba"
# Output: 4
# Explanation:
# Two possible partitions are ("a","ba","cab","a") and ("ab","a","ca","ba").
# It can be shown that 4 is the minimum number of substrings needed.
#
# Example 2:
#
# Input: s = "ssssss"
# Output: 6
# Explanation:
# The only valid partition is ("s","s","s","s","s","s").
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# s consists of only English lowercase letters.
#

# @lc code=start
class Solution:
    def partitionString(self, s: str) -> int:
        """
        Interview explanation:
        Partition s into minimum substrings with all unique characters.

        Algorithm:
        - Greedy: grow current set; on duplicate start a new partition.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        seen = set()
        ans = 1
        for ch in s:
            if ch in seen:
                ans += 1
                seen = {ch}
            else:
                seen.add(ch)
        return ans

    def partitionString_bit(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: bitset for the current partition's characters.

        Algorithm:
        - Mask of seen letters; reset mask and +1 partition on conflict.

        Complexity: O(n) time, O(1) space.
        """
        mask = 0
        ans = 1
        for ch in s:
            bit = 1 << (ord(ch) - 97)
            if mask & bit:
                ans += 1
                mask = bit
            else:
                mask |= bit
        return ans
# @lc code=end
