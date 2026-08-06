#
# @lc app=leetcode id=3853 lang=python3
#
# [3853] Merge Close Characters
#
# https://leetcode.com/problems/merge-close-characters/description/
#
# algorithms
# Medium (54.85%)
# Likes:    82
# Dislikes: 13
# Total Accepted:    29.7K
# Total Submissions: 54.1K
# Testcase Example:  "\"abca\"\n3"
#
#
# You are given a string s consisting of lowercase English letters and an
# integer k.
#
# Two equal characters in the current string s are considered close if the
# distance between their indices is at most k.
#
# When two characters are close, the right one merges into the left.
# Merges happen one at a time, and after each merge, the string updates
# until no more merges are possible.
#
# Return the resulting string after performing all possible merges.
#
# Note: If multiple merges are possible, always merge the pair with the
# smallest left index. If multiple pairs share the smallest left index,
# choose the pair with the smallest right index.
#
# Example 1:
#
# Input: s = "abca", k = 3
#
# Output: "abc"
#
# Explanation:
#
# ​​​​​​​Characters 'a' at indices i = 0 and i = 3 are close as 3 - 0 = 3
# <= k.
#
# Merge them into the left 'a' and s = "abc".
#
# No other equal characters are close, so no further merges occur.
#
# Example 2:
#
# Input: s = "aabca", k = 2
#
# Output: "abca"
#
# Explanation:
#
# Characters 'a' at indices i = 0 and i = 1 are close as 1 - 0 = 1 <= k.
#
# Merge them into the left 'a' and s = "abca".
#
# Now the remaining 'a' characters at indices i = 0 and i = 3 are not
# close as k < 3, so no further merges occur.
#
# Example 3:
#
# Input: s = "yybyzybz", k = 2
#
# Output: "ybzybz"
#
# Explanation:
#
# Characters 'y' at indices i = 0 and i = 1 are close as 1 - 0 = 1 <= k.
#
# Merge them into the left 'y' and s = "ybyzybz".
#
# Now the characters 'y' at indices i = 0 and i = 2 are close as 2 - 0 = 2
# <= k.
#
# Merge them into the left 'y' and s = "ybzybz".
#
# No other equal characters are close, so no further merges occur.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# 1 <= k <= s.length
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def mergeCharacters(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Equal characters within distance k merge right into left, preferring
        the leftmost pair. Building the result left-to-right while skipping
        chars close to their last kept occurrence is equivalent.

        Algorithm:
        - Track last index of each char in the built string.
        - Append c unless last[c] exists and cur - last[c] <= k.

        Complexity: O(n) time, O(|Σ|) space.
        """
        last: dict[str, int] = {}
        ans: list[str] = []
        for c in s:
            cur = len(ans)
            if c in last and cur - last[c] <= k:
                continue
            ans.append(c)
            last[c] = cur
        return "".join(ans)
# @lc code=end
