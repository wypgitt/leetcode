#
# @lc app=leetcode id=3104 lang=python3
#
# [3104] Find Longest Self-Contained Substring
#
# https://leetcode.com/problems/find-longest-self-contained-substring/description/
#
# algorithms
# Hard (58.43%)
# Likes:    19
# Dislikes: 6
# Total Accepted:    3.1K
# Total Submissions: 5.3K
# Testcase Example:  "\"abba\""
#
#
# Given a string s, your task is to find the length of the longest
# self-contained substring of s.
#
# A substring t of a string s is called self-contained if t != s and for
# every character in t, it doesn't exist in the rest of s.
#
# Return the length of the longest self-contained substring of s if it
# exists, otherwise, return -1.
#
# Example 1:
#
# Input: s = "abba"
#
# Output: 2
#
# Explanation:
#
# Let's check the substring "bb". You can see that no other "b" is outside
# of this substring. Hence the answer is 2.
#
# Example 2:
#
# Input: s = "abab"
#
# Output: -1
#
# Explanation:
#
# Every substring we choose does not satisfy the described property (there
# is some character which is inside and outside of that substring). So the
# answer would be -1.
#
# Example 3:
#
# Input: s = "abacd"
#
# Output: 4
#
# Explanation:
#
# Let's check the substring "abac". There is only one character outside of
# this substring and that is "d". There is no "d" inside the chosen
# substring, so it satisfies the condition and the answer is 4.
#
# Constraints:
#
# 2 <= s.length <= 5 * 10^4
#
# s consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def maxSubstringLength(self, s: str) -> int:
        """
        Interview explanation:
        Self-contained substring uses a set of letters that never appear outside
        it, and must be a proper substring. Maximize its length (else -1).

        Algorithm:
        - Record first/last index of each letter.
        - Start only at first occurrences; expand right, forcing inclusion of
          each letter's full span; when end equals required max and < n, update.

        Complexity: O(n * |Σ|) time, O(|Σ|) space.
        """
        first, last = {}, {}
        for i, c in enumerate(s):
            if c not in first:
                first[c] = i
            last[c] = i
        ans, n = -1, len(s)
        for i in first.values():
            mx = last[s[i]]
            for j in range(i, n):
                a, b = first[s[j]], last[s[j]]
                if a < i:
                    break
                mx = max(mx, b)
                if mx == j and j - i + 1 < n:
                    ans = max(ans, j - i + 1)
        return ans

    def maxSubstringLength_window(self, s: str) -> int:
        """
        Interview explanation:
        Equivalent to longest substring whose letter multiset equals the global
        multiset for those letters, excluding the full string (like LC 395).

        Algorithm:
        - For unique-letter count n = 1..26, sliding window with that many
          distinct letters; accept windows where every letter is complete.

        Complexity: O(n * |Σ|) time, O(|Σ|) space.
        """
        from collections import Counter

        all_count = Counter(s)
        ans = -1
        for n_unique in range(1, 27):
            count = Counter()
            unique = complete = 0
            l = 0
            for r, c in enumerate(s):
                count[c] += 1
                if count[c] == 1:
                    unique += 1
                if count[c] == all_count[c]:
                    complete += 1
                while unique > n_unique:
                    if count[s[l]] == all_count[s[l]]:
                        complete -= 1
                    count[s[l]] -= 1
                    if count[s[l]] == 0:
                        unique -= 1
                    l += 1
                if complete == n_unique and r - l + 1 < len(s):
                    ans = max(ans, r - l + 1)
        return ans
# @lc code=end
