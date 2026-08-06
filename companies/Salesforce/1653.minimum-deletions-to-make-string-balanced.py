#
# @lc app=leetcode id=1653 lang=python3
#
# [1653] Minimum Deletions to Make String Balanced
#
# https://leetcode.com/problems/minimum-deletions-to-make-string-balanced/description/
#
# algorithms
# Medium (68.16%)
# Likes:    2631
# Dislikes: 83
# Total Accepted:    296K
# Total Submissions: 434K
# Testcase Example:  "\"aababbab\""
#
# You are given a string s consisting only of characters 'a' and 'b'.
#
# You can delete any number of characters in s to make s balanced. s is
# balanced if there is no pair of indices (i,j) such that i < j and s[i] = 'b'
# and s[j]= 'a'.
#
# Return the minimum number of deletions needed to make s balanced.
#
# Example 1:
#
# Input: s = "aababbab"
# Output: 2
# Explanation: You can either:
# Delete the characters at 0-indexed positions 2 and 6 ("aababbab" ->
# "aaabbb"), or
# Delete the characters at 0-indexed positions 3 and 6 ("aababbab" ->
# "aabbbb").
#
# Example 2:
#
# Input: s = "bbaaaaabb"
# Output: 2
# Explanation: The only solution is to delete the first two characters.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is 'a' or 'b'.
#

# @lc code=start
class Solution:
    def minimumDeletions(self, s: str) -> int:
        """
        Interview explanation:
        Make string balanced: no "ba" as subsequence of form b...a (all a's before
        all b's). Count deletions: track how many b's seen; each a can delete that
        a or delete all prior b's — take running min.

        Algorithm (one pass):
        - b_count=0, ans=0; for c in s: if c=='b': b_count++ else ans=min(ans+1,b_count)

        Complexity: O(n) time, O(1) space.
        """
        b_count = ans = 0
        for c in s:
            if c == "b":
                b_count += 1
            else:
                ans = min(ans + 1, b_count)
        return ans

    def minimumDeletions_prefix(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: for each split, delete all b's left of split and a's right;
        take min over split points (including ends).

        Algorithm:
        - Pref b counts / suff a counts; min over i of left_b + right_a.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        left_b = [0] * (n + 1)
        for i, c in enumerate(s):
            left_b[i + 1] = left_b[i] + (c == "b")
        right_a = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            right_a[i] = right_a[i + 1] + (s[i] == "a")
        return min(left_b[i] + right_a[i] for i in range(n + 1))
# @lc code=end
