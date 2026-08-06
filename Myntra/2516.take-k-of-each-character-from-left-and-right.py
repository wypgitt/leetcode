#
# @lc app=leetcode id=2516 lang=python3
#
# [2516] Take K of Each Character From Left and Right
#
# https://leetcode.com/problems/take-k-of-each-character-from-left-and-right/description/
#
# algorithms
# Medium (51.47%)
# Likes:    1554
# Dislikes: 177
# Total Accepted:    117.7K
# Total Submissions: 228.7K
# Testcase Example:  "\"aabaaaacaabc\"\n2"
#
# You are given a string s consisting of the characters 'a', 'b', and 'c' and a
# non-negative integer k. Each minute, you may take either the leftmost
# character of s, or the rightmost character of s.
#
# Return the minimum number of minutes needed for you to take at least k of each
# character, or return -1 if it is not possible to take k of each character.
#
#
#
# Example 1:
#
# Input: s = "aabaaaacaabc", k = 2
# Output: 8
# Explanation:
# Take three characters from the left of s. You now have two 'a' characters, and
# one 'b' character.
# Take five characters from the right of s. You now have four 'a' characters,
# two 'b' characters, and two 'c' characters.
# A total of 3 + 5 = 8 minutes is needed.
# It can be proven that 8 is the minimum number of minutes needed.
#
# Example 2:
#
# Input: s = "a", k = 1
# Output: -1
# Explanation: It is not possible to take one 'b' or 'c' so return -1.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# s consists of only the letters 'a', 'b', and 'c'.
#
#
# 0 <= k <= s.length
#

# @lc code=start
class Solution:
    def takeCharacters(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Take letters only from ends; minimize minutes to get >= k of a, b, and c.

        Algorithm:
        (sliding window)
        - Equivalent to maximize a middle window we keep, with outside still having
          >= k of each: window count[c] <= total[c]-k for all c.

        Complexity: O(n) time, O(1) space.
        """
        if k == 0:
            return 0
        total = [0, 0, 0]
        for ch in s:
            total[ord(ch) - ord('a')] += 1
        if any(c < k for c in total):
            return -1

        limit = [c - k for c in total]
        n = len(s)
        left = 0
        window = [0, 0, 0]
        max_keep = 0
        for right, ch in enumerate(s):
            idx = ord(ch) - ord('a')
            window[idx] += 1
            while window[0] > limit[0] or window[1] > limit[1] or window[2] > limit[2]:
                window[ord(s[left]) - ord('a')] -= 1
                left += 1
            max_keep = max(max_keep, right - left + 1)
        return n - max_keep
# @lc code=end
