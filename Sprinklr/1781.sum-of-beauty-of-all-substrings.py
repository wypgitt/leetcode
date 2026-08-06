#
# @lc app=leetcode id=1781 lang=python3
#
# [1781] Sum of Beauty of All Substrings
#
# https://leetcode.com/problems/sum-of-beauty-of-all-substrings/description/
#
# algorithms
# Medium (74.59%)
# Likes:    1648
# Dislikes: 225
# Total Accepted:    213K
# Total Submissions: 285K
# Testcase Example:  "\"aabcb\""
#
# The beauty of a string is the difference in frequencies between the most
# frequent and least frequent characters.
#
# For example, the beauty of "abaacc" is 3 - 1 = 2.
#
# Given a string s, return the sum of beauty of all of its substrings.
#
# Example 1:
#
# Input: s = "aabcb"
# Output: 5
# Explanation: The substrings with non-zero beauty are
# ["aab","aabc","aabcb","abcb","bcb"], each with beauty equal to 1.
#
# Example 2:
#
# Input: s = "aabcbaa"
# Output: 17
#
# Constraints:
#
# 1 <= s.length <=^ 500
#
# s consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def beautySum(self, s: str) -> int:
        """
        Interview explanation:
        Beauty of a substring = maxfreq − minfreq among chars present. Sum
        beauty over all O(n^2) substrings. For each left endpoint, expand
        right while maintaining a frequency map (26 letters).

        Algorithm:
        - For i: freq=[0]*26; for j=i..n-1: freq[s[j]]++; beauty += max(freq)-min(nonzero).

        Complexity: O(n^2 * Σ) time, O(Σ) space.
        """
        n = len(s)
        ans = 0
        for i in range(n):
            freq = [0] * 26
            for j in range(i, n):
                freq[ord(s[j]) - 97] += 1
                present = [f for f in freq if f]
                ans += max(present) - min(present)
        return ans

    def beautySum_opt(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: same expansion but track maxfreq and scan 26 for minfreq
        each step (avoids building present list).

        Algorithm:
        - Maintain freq + running maxf; minf = min of positive freqs.

        Complexity: O(n^2 * Σ) time, O(Σ) space.
        """
        n = len(s)
        ans = 0
        for i in range(n):
            freq = [0] * 26
            maxf = 0
            for j in range(i, n):
                k = ord(s[j]) - 97
                freq[k] += 1
                if freq[k] > maxf:
                    maxf = freq[k]
                minf = min(f for f in freq if f)
                ans += maxf - minf
        return ans
# @lc code=end
