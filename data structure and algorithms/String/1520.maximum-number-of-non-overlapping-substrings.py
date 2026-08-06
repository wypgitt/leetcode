#
# @lc app=leetcode id=1520 lang=python3
#
# [1520] Maximum Number of Non-Overlapping Substrings
#
# https://leetcode.com/problems/maximum-number-of-non-overlapping-substrings/description/
#
# algorithms
# Hard (43.57%)
# Likes:    927
# Dislikes: 88
# Total Accepted:    28.1K
# Total Submissions: 64.4K
# Testcase Example:  "\"adefaddaccc\""
#
# Given a string s of lowercase letters, you need to find the maximum number of
# non-empty substrings of s that meet the following conditions:
#
# The substrings do not overlap, that is for any two substrings s[i..j] and
# s[x..y], either j < x or i > y is true.
#
# A substring that contains a certain character c must also contain all
# occurrences of c.
#
# Find the maximum number of substrings that meet the above conditions. If
# there are multiple solutions with the same number of substrings, return the
# one with minimum total length. It can be shown that there exists a unique
# solution of minimum total length.
#
# Notice that you can return the substrings in any order.
#
# Example 1:
#
# Input: s = "adefaddaccc"
# Output: ["e","f","ccc"]
# Explanation: The following are all the possible substrings that meet the
# conditions:
# [
# "adefaddaccc"
# "adefadda",
# "ef",
# "e",
# "f",
# "ccc",
# ]
# If we choose the first string, we cannot choose anything else and we'd get
# only 1. If we choose "adefadda", we are left with "ccc" which is the only one
# that doesn't overlap, thus obtaining 2 substrings. Notice also, that it's not
# optimal to choose "ef" since it can be split into two. Therefore, the optimal
# way is to choose ["e","f","ccc"] which gives us 3 substrings. No other
# solution of the same number of substrings exist.
#
# Example 2:
#
# Input: s = "abbaccd"
# Output: ["d","bb","cc"]
# Explanation: Notice that while the set of substrings ["d","abba","cc"] also
# has length 3, it's considered incorrect since it has larger total length.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def maxNumOfSubstrings(self, s: str) -> List[str]:
        """
        Interview explanation:
        Find maximum number of non-overlapping substrings such that each
        character's all occurrences lie inside its substring (minimal "complete"
        intervals). For each char, expand [first,last] until all chars in range
        are fully contained; greedily take intervals by earliest end.

        Algorithm:
        - first/last for each char; expand intervals; sort by end; greedy pick.

        Complexity: O(26*n) time, O(26) space + output.
        """
        first = {}
        last = {}
        for i, ch in enumerate(s):
            if ch not in first:
                first[ch] = i
            last[ch] = i

        intervals = []
        for ch in first:
            l, r = first[ch], last[ch]
            i = l
            valid = True
            while i <= r:
                c = s[i]
                if first[c] < l:
                    valid = False
                    break
                r = max(r, last[c])
                i += 1
            if valid:
                intervals.append((l, r))

        intervals.sort(key=lambda x: x[1])
        ans = []
        prev_end = -1
        for l, r in intervals:
            if l > prev_end:
                ans.append(s[l : r + 1])
                prev_end = r
        return ans
# @lc code=end
