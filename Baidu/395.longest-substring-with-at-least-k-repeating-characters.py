#
# @lc app=leetcode id=395 lang=python3
#
# [395] Longest Substring with At Least K Repeating Characters
#
# https://leetcode.com/problems/longest-substring-with-at-least-k-repeating-characters/description/
#
# algorithms
# Medium (46.51%)
# Likes:    6800
# Dislikes: 574
# Total Accepted:    309K
# Total Submissions: 665K
# Testcase Example:  "\"aaabb\""
#
# Given a string s and an integer k, return the length of the longest substring
# of s such that the frequency of each character in this substring is greater
# than or equal to k.
#
# if no such substring exists, return 0.
#
# Example 1:
#
# Input: s = "aaabb", k = 3
# Output: 3
# Explanation: The longest substring is "aaa", as 'a' is repeated 3 times.
#
# Example 2:
#
# Input: s = "ababbc", k = 2
# Output: 5
# Explanation: The longest substring is "ababb", as 'a' is repeated 2 times and
# 'b' is repeated 3 times.
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of only lowercase English letters.
#
# 1 <= k <= 10^5
#

# @lc code=start
from collections import Counter


class Solution:
    def longestSubstring(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Divide and conquer: if any char has total count < k, it can never
        appear in a valid substring — split s on those chars and recurse.
        Base: empty → 0; all counts ≥ k → len(s).

        Algorithm:
        - Count chars; find a splitter with count < k.
        - If none, return len(s); else max over segments split by that char.

        Complexity: O(n * Σ) time (Σ≤26), O(n) recursion/stack space.
        """
        if not s:
            return 0
        count = Counter(s)
        for ch, freq in count.items():
            if freq < k:
                return max(
                    (self.longestSubstring(part, k) for part in s.split(ch)),
                    default=0,
                )
        return len(s)

    def longestSubstringSliding(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Alternate: sliding window over unique-char budgets 1..26. For each
        target unique count, expand/shrink while tracking freqs and how many
        chars meet ≥ k; update max when unique==target and all ≥ k.

        Complexity: O(26 * n) = O(n) time, O(1) space.
        """
        n = len(s)
        ans = 0
        for target_unique in range(1, 27):
            freq = [0] * 26
            left = unique = at_least_k = 0
            for right, ch in enumerate(s):
                idx = ord(ch) - 97
                if freq[idx] == 0:
                    unique += 1
                freq[idx] += 1
                if freq[idx] == k:
                    at_least_k += 1
                while unique > target_unique:
                    lidx = ord(s[left]) - 97
                    if freq[lidx] == k:
                        at_least_k -= 1
                    freq[lidx] -= 1
                    if freq[lidx] == 0:
                        unique -= 1
                    left += 1
                if unique == target_unique and unique == at_least_k:
                    ans = max(ans, right - left + 1)
        return ans
# @lc code=end
