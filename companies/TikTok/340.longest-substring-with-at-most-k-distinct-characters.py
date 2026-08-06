#
# @lc app=leetcode id=340 lang=python3
#
# [340] Longest Substring with At Most K Distinct Characters
#
# https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/description/
#
# algorithms
# Medium (50.09%)
# Likes:    2905
# Dislikes: 81
# Total Accepted:    403.7K
# Total Submissions: 806K
# Testcase Example:  "\"eceba\"\n2"
#
#
# Given a string s and an integer k, return the length of the longest
# substring of s that contains at most k distinct characters.
#
# Example 1:
#
# Input: s = "eceba", k = 2
# Output: 3
# Explanation: The substring is "ece" with length 3.
#
# Example 2:
#
# Input: s = "aa", k = 1
# Output: 2
# Explanation: The substring is "aa" with length 2.
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^4
#
# 0 <= k <= 50
#
# @lc code=start
from collections import defaultdict


class Solution:
    def lengthOfLongestSubstringKDistinct(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Sliding window with a frequency map: expand right; when distinct count
        exceeds k, shrink left until valid. Track max window length.

        Algorithm:
        - right grows; freq[s[right]]++.
        - While len(freq) > k: decrement/remove s[left], left++.
        - Update best = max(best, right - left + 1).

        Complexity: O(n) time, O(k) space.
        """
        if k == 0:
            return 0
        freq: dict[str, int] = defaultdict(int)
        left = 0
        best = 0
        for right, ch in enumerate(s):
            freq[ch] += 1
            while len(freq) > k:
                freq[s[left]] -= 1
                if freq[s[left]] == 0:
                    del freq[s[left]]
                left += 1
            best = max(best, right - left + 1)
        return best
# @lc code=end
