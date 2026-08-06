#
# @lc app=leetcode id=2287 lang=python3
#
# [2287] Rearrange Characters to Make Target String
#
# https://leetcode.com/problems/rearrange-characters-to-make-target-string/description/
#
# algorithms
# Easy (63.13%)
# Likes:    576
# Dislikes: 39
# Total Accepted:    64.8K
# Total Submissions: 102.7K
# Testcase Example:  "\"ilovecodingonleetcode\"\n\"code\""
#
# You are given two 0-indexed strings s and target. You can take some letters
# from s and rearrange them to form new strings.
#
# Return the maximum number of copies of target that can be formed by taking
# letters from s and rearranging them.
#
#
#
# Example 1:
#
# Input: s = "ilovecodingonleetcode", target = "code"
# Output: 2
# Explanation:
# For the first copy of "code", take the letters at indices 4, 5, 6, and 7.
# For the second copy of "code", take the letters at indices 17, 18, 19, and 20.
# The strings that are formed are "ecod" and "code" which can both be rearranged
# into "code".
# We can make at most two copies of "code", so we return 2.
#
# Example 2:
#
# Input: s = "abcba", target = "abc"
# Output: 1
# Explanation:
# We can make one copy of "abc" by taking the letters at indices 0, 1, and 2.
# We can make at most one copy of "abc", so we return 1.
# Note that while there is an extra 'a' and 'b' at indices 3 and 4, we cannot
# reuse the letter 'c' at index 2, so we cannot make a second copy of "abc".
#
# Example 3:
#
# Input: s = "abbaccaddaeea", target = "aaaaa"
# Output: 1
# Explanation:
# We can make one copy of "aaaaa" by taking the letters at indices 0, 3, 6, 9,
# and 12.
# We can make at most one copy of "aaaaa", so we return 1.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 100
#
#
# 1 <= target.length <= 10
#
#
# s and target consist of lowercase English letters.
#
#
#
# Note: This question is the same as  1189: Maximum Number of Balloons.
#

# @lc code=start
from collections import Counter


class Solution:
    def rearrangeCharacters(self, s: str, target: str) -> int:
        """
        Interview explanation:
        Max copies of target formable from letters in s (each letter used once).

        Algorithm:
        - For each char in target, floor(count_s / count_target); take min.

        Complexity: O(|s| + |target|) time, O(1) space.
        """
        cs, ct = Counter(s), Counter(target)
        return min(cs[c] // ct[c] for c in ct)
# @lc code=end
