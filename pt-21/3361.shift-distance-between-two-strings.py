#
# @lc app=leetcode id=3361 lang=python3
#
# [3361] Shift Distance Between Two Strings
#
# https://leetcode.com/problems/shift-distance-between-two-strings/description/
#
# algorithms
# Medium (53.91%)
# Likes:    71
# Dislikes: 47
# Total Accepted:    18K
# Total Submissions: 33.4K
# Testcase Example:  "\"abab\"\n\"baba\"\n[100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]\n[1,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]"
#
#
# You are given two strings s and t of the same length, and two integer
# arrays nextCost and previousCost.
#
# In one operation, you can pick any index i of s, and perform either one
# of the following actions:
#
# Shift s[i] to the next letter in the alphabet. If s[i] == 'z', you
# should replace it with 'a'. This operation costs nextCost[j] where j is
# the index of s[i] in the alphabet.
#
# Shift s[i] to the previous letter in the alphabet. If s[i] == 'a', you
# should replace it with 'z'. This operation costs previousCost[j] where j
# is the index of s[i] in the alphabet.
#
# The shift distance is the minimum total cost of operations required to
# transform s into t.
#
# Return the shift distance from s to t.
#
# Example 1:
#
# Input: s = "abab", t = "baba", nextCost =
# [100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], previousCost =
# [1,100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#
# Output: 2
#
# Explanation:
#
# We choose index i = 0 and shift s[0] 25 times to the previous character
# for a total cost of 1.
#
# We choose index i = 1 and shift s[1] 25 times to the next character for
# a total cost of 0.
#
# We choose index i = 2 and shift s[2] 25 times to the previous character
# for a total cost of 1.
#
# We choose index i = 3 and shift s[3] 25 times to the next character for
# a total cost of 0.
#
# Example 2:
#
# Input: s = "leet", t = "code", nextCost =
# [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], previousCost =
# [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
#
# Output: 31
#
# Explanation:
#
# We choose index i = 0 and shift s[0] 9 times to the previous character
# for a total cost of 9.
#
# We choose index i = 1 and shift s[1] 10 times to the next character for
# a total cost of 10.
#
# We choose index i = 2 and shift s[2] 1 time to the previous character
# for a total cost of 1.
#
# We choose index i = 3 and shift s[3] 11 times to the next character for
# a total cost of 11.
#
# Constraints:
#
# 1 <= s.length == t.length <= 10^5
#
# s and t consist only of lowercase English letters.
#
# nextCost.length == previousCost.length == 26
#
# 0 <= nextCost[i], previousCost[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def shiftDistance(self, s: str, t: str, nextCost: List[int], previousCost: List[int]) -> int:
        """
        Interview explanation:
        Each position transforms independently. For letters a -> b, take the cheaper
        of walking next-cost forward or previous-cost backward on the alphabet ring.

        Algorithm:
        - Precompute 26x26 min costs via both directions (O(26^2)).
        - Sum min cost over all positions.

        Complexity: O(|s| + 26^2) time, O(26^2) space.
        """
        inf = 10**30
        dist = [[inf] * 26 for _ in range(26)]
        for a in range(26):
            dist[a][a] = 0
            c = 0
            cur = a
            for _ in range(25):
                c += nextCost[cur]
                cur = (cur + 1) % 26
                dist[a][cur] = min(dist[a][cur], c)
            c = 0
            cur = a
            for _ in range(25):
                c += previousCost[cur]
                cur = (cur - 1) % 26
                dist[a][cur] = min(dist[a][cur], c)

        return sum(dist[ord(a) - 97][ord(b) - 97] for a, b in zip(s, t))

    def shiftDistance_prefix(self, s: str, t: str, nextCost: List[int], previousCost: List[int]) -> int:
        """
        Interview explanation:
        Alternate: ring prefix sums for forward/backward segment costs.

        Algorithm:
        - next_pref[i] = sum(nextCost[:i]); prev similarly.
        - For a -> b, forward = wrap segment on next_pref; backward on prev_pref.

        Complexity: O(|s|) time after O(26) preprocess, O(1) extra space.
        """
        next_pref = [0] * 27
        prev_pref = [0] * 27
        for i in range(26):
            next_pref[i + 1] = next_pref[i] + nextCost[i]
            prev_pref[i + 1] = prev_pref[i] + previousCost[i]
        total_next = next_pref[26]
        total_prev = prev_pref[26]

        def forward(a: int, b: int) -> int:
            if a <= b:
                return next_pref[b] - next_pref[a]
            return total_next - next_pref[a] + next_pref[b]

        def backward(a: int, b: int) -> int:
            # pay previousCost at a, a-1, ..., b+1
            if a == b:
                return 0
            if a > b:
                return prev_pref[a + 1] - prev_pref[b + 1]
            return prev_pref[a + 1] + (total_prev - prev_pref[b + 1])

        ans = 0
        for x, y in zip(s, t):
            a, b = ord(x) - 97, ord(y) - 97
            ans += min(forward(a, b), backward(a, b))
        return ans
# @lc code=end
