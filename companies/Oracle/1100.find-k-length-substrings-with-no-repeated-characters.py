#
# @lc app=leetcode id=1100 lang=python3
#
# [1100] Find K-Length Substrings With No Repeated Characters
#
# https://leetcode.com/problems/find-k-length-substrings-with-no-repeated-characters/description/
#
# algorithms
# Medium (76.46%)
# Likes:    609
# Dislikes: 11
# Total Accepted:    57.4K
# Total Submissions: 75.1K
# Testcase Example:  "\"havefunonleetcode\"\n5"
#
#
# Given a string s and an integer k, return the number of substrings in s
# of length k with no repeated characters.
#
# Example 1:
#
# Input: s = "havefunonleetcode", k = 5
# Output: 6
# Explanation: There are 6 substrings they are:
# 'havef','avefu','vefun','efuno','etcod','tcode'.
#
# Example 2:
#
# Input: s = "home", k = 5
# Output: 0
# Explanation: Notice k can be larger than the length of s. In this case,
# it is not possible to find any substring.
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of lowercase English letters.
#
# 1 <= k <= 10^4
#
# @lc code=start
class Solution:
    def numKLenSubstrNoRepeats(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Premium. Count substrings of length k with all unique characters.
        Sliding window: maintain a window with distinct chars; when window
        size reaches k, count +1 and shrink from left.

        Algorithm (sliding window):
        - left=0; freq map; for right in range(n): add s[right]; while duplicate
          or window > k: remove s[left].
        - If window size == k: ans++.

        Complexity: O(n) time, O(Σ) space (alphabet).
        """
        if k > len(s):
            return 0
        from collections import defaultdict

        freq = defaultdict(int)
        left = ans = 0
        for right, ch in enumerate(s):
            freq[ch] += 1
            while freq[ch] > 1 or right - left + 1 > k:
                freq[s[left]] -= 1
                left += 1
            if right - left + 1 == k:
                ans += 1
        return ans
# @lc code=end
