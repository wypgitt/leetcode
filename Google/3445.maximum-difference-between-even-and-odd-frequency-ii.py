#
# @lc app=leetcode id=3445 lang=python3
#
# [3445] Maximum Difference Between Even and Odd Frequency II
#
# https://leetcode.com/problems/maximum-difference-between-even-and-odd-frequency-ii/description/
#
# algorithms
# Hard (48.63%)
# Likes:    397
# Dislikes: 105
# Total Accepted:    59.1K
# Total Submissions: 121.6K
# Testcase Example:  "\"12233\"\n4"
#
#
# You are given a string s and an integer k. Your task is to find the
# maximum difference between the frequency of two characters, freq[a] -
# freq[b], in a substring subs of s, such that:
#
# subs has a size of at least k.
#
# Character a has an odd frequency in subs.
#
# Character b has a non-zero even frequency in subs.
#
# Return the maximum difference.
#
# Note that subs can contain more than 2 distinct characters.
#
# Example 1:
#
# Input: s = "12233", k = 4
#
# Output: -1
#
# Explanation:
#
# For the substring "12233", the frequency of '1' is 1 and the frequency
# of '3' is 2. The difference is 1 - 2 = -1.
#
# Example 2:
#
# Input: s = "1122211", k = 3
#
# Output: 1
#
# Explanation:
#
# For the substring "11222", the frequency of '2' is 3 and the frequency
# of '1' is 2. The difference is 3 - 2 = 1.
#
# Example 3:
#
# Input: s = "110", k = 3
#
# Output: -1
#
# Constraints:
#
# 3 <= s.length <= 3 * 10^4
#
# s consists only of digits '0' to '4'.
#
# The input is generated that at least one substring has a character with
# an even frequency and a character with an odd frequency.
#
# 1 <= k <= s.length
#

# @lc code=start

from math import inf


class Solution:
    def maxDifference(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Maximize freq[a]-freq[b] over substrings of length >= k where a is odd and
        b is nonzero even. Alphabet is only digits 0..4.

        Algorithm:
        - Enumerate ordered pairs (a,b). Slide right endpoint; shrink left while
          length>=k and window has >=2 b's, storing min prefix(a)-prefix(b) by
          parity of those prefixes.
        - Candidate = curA-curB - min prefix with opposite a-parity and same b-parity
          (so a ends odd, b ends even).

        Complexity: O(n) time (20 pairs), O(1) extra space.
        """
        arr = list(map(int, s))
        ans = -inf
        for a in range(5):
            for b in range(5):
                if a == b:
                    continue
                cur_a = cur_b = 0
                pre_a = pre_b = 0
                t = [[inf, inf], [inf, inf]]
                left = -1
                for r, x in enumerate(arr):
                    cur_a += x == a
                    cur_b += x == b
                    while r - left >= k and cur_b - pre_b >= 2:
                        t[pre_a & 1][pre_b & 1] = min(
                            t[pre_a & 1][pre_b & 1], pre_a - pre_b
                        )
                        left += 1
                        pre_a += arr[left] == a
                        pre_b += arr[left] == b
                    ans = max(ans, cur_a - cur_b - t[cur_a & 1 ^ 1][cur_b & 1])
        return int(ans)
# @lc code=end
