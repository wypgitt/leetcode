#
# @lc app=leetcode id=1542 lang=python3
#
# [1542] Find Longest Awesome Substring
#
# https://leetcode.com/problems/find-longest-awesome-substring/description/
#
# algorithms
# Hard (47.28%)
# Likes:    904
# Dislikes: 16
# Total Accepted:    21.7K
# Total Submissions: 45.9K
# Testcase Example:  "\"3242415\""
#
# You are given a string s. An awesome substring is a non-empty substring of s
# such that we can make any number of swaps in order to make it a palindrome.
#
# Return the length of the maximum length awesome substring of s.
#
# Example 1:
#
# Input: s = "3242415"
# Output: 5
# Explanation: "24241" is the longest awesome substring, we can form the
# palindrome "24142" with some swaps.
#
# Example 2:
#
# Input: s = "12345678"
# Output: 1
#
# Example 3:
#
# Input: s = "213123"
# Output: 6
# Explanation: "213123" is the longest awesome substring, we can form the
# palindrome "231132" with some swaps.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of digits.
#

# @lc code=start
class Solution:
    def longestAwesome(self, s: str) -> int:
        """
        Interview explanation:
        Longest substring that can be rearranged into a palindrome = at most
        one odd-count digit. Track XOR bitmask of digit parities; for each
        prefix mask, best length is i - first[mask] (all even) or i-first[mask^bit]
        (one odd digit).

        Algorithm:
        - first[0]=-1; mask=0; for i,ch: mask^=1<<d; update ans with mask and
          mask^(1<<b) for b=0..9; record first occurrence of mask.

        Complexity: O(n * 10) time, O(2^10) space.
        """
        first = {0: -1}
        mask = 0
        ans = 0
        for i, ch in enumerate(s):
            mask ^= 1 << (ord(ch) - 48)
            if mask in first:
                ans = max(ans, i - first[mask])
            else:
                first[mask] = i
            for b in range(10):
                m2 = mask ^ (1 << b)
                if m2 in first:
                    ans = max(ans, i - first[m2])
        return ans
# @lc code=end
