#
# @lc app=leetcode id=1358 lang=python3
#
# [1358] Number of Substrings Containing All Three Characters
#
# https://leetcode.com/problems/number-of-substrings-containing-all-three-characters/description/
#
# algorithms
# Medium (74.39%)
# Likes:    4806
# Dislikes: 93
# Total Accepted:    609K
# Total Submissions: 818K
# Testcase Example:  "\"abcabc\""
#
# Given a string s consisting only of characters a, b and c.
#
# Return the number of substrings containing at least one occurrence of all
# these characters a, b and c.
#
# Example 1:
#
# Input: s = "abcabc"
# Output: 10
# Explanation: The substrings containing at least one occurrence of the
# characters a, b and c are "abc", "abca", "abcab", "abcabc", "bca", "bcab",
# "bcabc", "cab", "cabc" and "abc" (again).
#
# Example 2:
#
# Input: s = "aaacb"
# Output: 3
# Explanation: The substrings containing at least one occurrence of the
# characters a, b and c are "aaacb", "aacb" and "acb".
#
# Example 3:
#
# Input: s = "abc"
# Output: 1
#
# Constraints:
#
# 3 <= s.length <= 5 x 10^4
#
# s only consists of 'a', 'b' or 'c' characters.
#

# @lc code=start

class Solution:
    def numberOfSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Count substrings containing at least one a,b,c. Sliding window: once
        [l,r] is valid, every extension of r still valid for fixed l... better:
        for each r, find smallest l so [l,r] has all three; then all starts
        0..l contribute.

        Algorithm:
        - last positions of a,b,c; for each r update last[s[r]]
          if all seen: ans += 1+min(last values)

        Complexity: O(n) time, O(1) space.
        """
        last = [-1, -1, -1]
        ans = 0
        for i, ch in enumerate(s):
            last[ord(ch) - ord("a")] = i
            if last[0] != -1 and last[1] != -1 and last[2] != -1:
                ans += 1 + min(last)
        return ans

    def numberOfSubstrings_window(self, s: str) -> int:
        """
        Interview explanation:
        Alternate classic two-pointer: expand r; while window has all three,
        every substring starting at l and ending ≥r is valid... actually:
        when valid, ans += n-r; then shrink l.

        Algorithm:
        - cnt of a,b,c; for r in range: add s[r]; while all>0: ans+=n-r; remove s[l]; l+=1

        Complexity: O(n) time, O(1) space.
        """
        from collections import Counter
        cnt = Counter()
        ans = l = 0
        n = len(s)
        for r, ch in enumerate(s):
            cnt[ch] += 1
            while cnt["a"] and cnt["b"] and cnt["c"]:
                ans += n - r
                cnt[s[l]] -= 1
                l += 1
        return ans
# @lc code=end
