#
# @lc app=leetcode id=942 lang=python3
#
# [942] DI String Match
#
# https://leetcode.com/problems/di-string-match/description/
#
# algorithms
# Easy (81.22%)
# Likes:    2633
# Dislikes: 1082
# Total Accepted:    216K
# Total Submissions: 266K
# Testcase Example:  "\"IDID\""
#
# A permutation perm of n + 1 integers of all the integers in the range [0, n]
# can be represented as a string s of length n where:
#
# s[i] == 'I' if perm[i] < perm[i + 1], and
#
# s[i] == 'D' if perm[i] > perm[i + 1].
#
# Given a string s, reconstruct the permutation perm and return it. If there
# are multiple valid permutations perm, return any of them.
#
# Example 1:
#
# Input: s = "IDID"
# Output: [0,4,1,3,2]
#
# Example 2:
#
# Input: s = "III"
# Output: [0,1,2,3]
#
# Example 3:
#
# Input: s = "DDI"
# Output: [3,2,0,1]
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either 'I' or 'D'.
#

# @lc code=start
from typing import List


class Solution:
    def diStringMatch(self, s: str) -> List[int]:
        """
        Interview explanation:
        Greedy with low/high pointers over [0..n]. 'I' takes current low
        (forces next larger); 'D' takes current high (forces next smaller);
        append remaining value at end.

        Algorithm:
        - lo, hi = 0, n; ans=[]
        - For 'I': ans.append(lo); lo+=1
        - For 'D': ans.append(hi); hi-=1
        - ans.append(lo)

        Complexity: O(n) time, O(n) space for output.
        """
        lo, hi = 0, len(s)
        ans = []
        for c in s:
            if c == 'I':
                ans.append(lo)
                lo += 1
            else:
                ans.append(hi)
                hi -= 1
        ans.append(lo)
        return ans
# @lc code=end

