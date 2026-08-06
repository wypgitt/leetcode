#
# @lc app=leetcode id=767 lang=python3
#
# [767] Reorganize String
#
# https://leetcode.com/problems/reorganize-string/description/
#
# algorithms
# Medium (57.41%)
# Likes:    9335
# Dislikes: 288
# Total Accepted:    625K
# Total Submissions: 1.1M
# Testcase Example:  "\"aab\""
#
# Given a string s, rearrange the characters of s so that any two adjacent
# characters are not the same.
#
# Return any possible rearrangement of s or return "" if not possible.
#
# Example 1:
#
# Input: s = "aab"
# Output: "aba"
#
# Example 2:
#
# Input: s = "aaab"
# Output: ""
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of lowercase English letters.
#


# @lc code=start
import heapq
from collections import Counter


class Solution:
    def reorganizeString(self, s: str) -> str:
        """
        Interview explanation:
        Greedy with max-heap of character frequencies: always place the most
        frequent remaining char that is not equal to the previous placed char.
        Impossible if any count > (n+1)//2.

        Algorithm:
        - If max count > (n+1)//2: return ""
        - Heap of (-count, char); while heap: pop most frequent; append; push
          previous leftover back if any

        Complexity: O(n log Σ) time, O(Σ) space for alphabet size Σ.
        """
        n = len(s)
        cnt = Counter(s)
        if max(cnt.values()) > (n + 1) // 2:
            return ""
        heap = [(-c, ch) for ch, c in cnt.items()]
        heapq.heapify(heap)
        ans = []
        prev_c, prev_ch = 0, ""
        while heap:
            c, ch = heapq.heappop(heap)
            ans.append(ch)
            if prev_c < 0:
                heapq.heappush(heap, (prev_c, prev_ch))
            prev_c, prev_ch = c + 1, ch
        return "".join(ans)
# @lc code=end

