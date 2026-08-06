#
# @lc app=leetcode id=1647 lang=python3
#
# [1647] Minimum Deletions to Make Character Frequencies Unique
#
# https://leetcode.com/problems/minimum-deletions-to-make-character-frequencies-unique/description/
#
# algorithms
# Medium (61.52%)
# Likes:    5072
# Dislikes: 76
# Total Accepted:    305K
# Total Submissions: 495K
# Testcase Example:  "\"aab\""
#
# A string s is called good if there are no two different characters in s that
# have the same frequency.
#
# Given a string s, return the minimum number of characters you need to delete
# to make s good.
#
# The frequency of a character in a string is the number of times it appears in
# the string. For example, in the string "aab", the frequency of 'a' is 2,
# while the frequency of 'b' is 1.
#
# Example 1:
#
# Input: s = "aab"
# Output: 0
# Explanation: s is already good.
#
# Example 2:
#
# Input: s = "aaabbbcc"
# Output: 2
# Explanation: You can delete two 'b's resulting in the good string "aaabcc".
# Another way it to delete one 'b' and one 'c' resulting in the good string
# "aaabbc".
#
# Example 3:
#
# Input: s = "ceabaacb"
# Output: 2
# Explanation: You can delete both 'c's resulting in the good string "eabaab".
# Note that we only care about characters that are still in the string at the
# end (i.e. frequency of 0 is ignored).
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def minDeletions(self, s: str) -> int:
        """
        Interview explanation:
        Make all character frequencies unique via deletions. Greedy: for each freq
        from high counts, decrease until unused.

        Algorithm (greedy set):
        - Count freqs; used set; for each freq while >0 and in used: freq--; ans++.
          then add freq if >0.

        Complexity: O(n + Σf) ~ O(n) time, O(Σf) space.
        """
        freq = list(Counter(s).values())
        used = set()
        ans = 0
        for f in freq:
            while f > 0 and f in used:
                f -= 1
                ans += 1
            if f > 0:
                used.add(f)
        return ans

    def minDeletions_sort(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: sort frequencies descending; ensure strictly decreasing by
        capping each next freq to prev-1.

        Algorithm (sort):
        - Sort freqs desc; for i>0: if freq[i]>=freq[i-1], reduce to max(0,freq[i-1]-1).

        Complexity: O(n + k log k) time.
        """
        freq = sorted(Counter(s).values(), reverse=True)
        ans = 0
        for i in range(1, len(freq)):
            if freq[i] >= freq[i - 1]:
                target = max(0, freq[i - 1] - 1)
                ans += freq[i] - target
                freq[i] = target
        return ans
# @lc code=end
