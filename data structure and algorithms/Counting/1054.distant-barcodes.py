#
# @lc app=leetcode id=1054 lang=python3
#
# [1054] Distant Barcodes
#
# https://leetcode.com/problems/distant-barcodes/description/
#
# algorithms
# Medium (49.28%)
# Likes:    1369
# Dislikes: 52
# Total Accepted:    60.1K
# Total Submissions: 122K
# Testcase Example:  "[1,1,1,2,2,2]"
#
# In a warehouse, there is a row of barcodes, where the i^th barcode is
# barcodes[i].
#
# Rearrange the barcodes so that no two adjacent barcodes are equal. You may
# return any answer, and it is guaranteed an answer exists.
#
# Example 1:
#
# Input: barcodes = [1,1,1,2,2,2]
# Output: [2,1,2,1,2,1]
#
# Example 2:
#
# Input: barcodes = [1,1,1,1,2,2,3,3]
# Output: [1,3,1,3,1,2,1,2]
#
# Constraints:
#
# 1 <= barcodes.length <= 10000
#
# 1 <= barcodes[i] <= 10000
#

# @lc code=start
from collections import Counter
import heapq
from typing import List


class Solution:
    def rearrangeBarcodes(self, barcodes: List[int]) -> List[int]:
        """
        Interview explanation:
        Rearrange so no two adjacent equal — place most frequent first into even
        slots then odd (or use max-heap greedy). Counting + fill by frequency.

        Algorithm:
        - Count; place most common into even indices first, then continue

        Complexity: O(n log k) or O(n + k log k), O(n) space.
        """
        n = len(barcodes)
        cnt = Counter(barcodes)
        ordered = sorted(cnt.keys(), key=lambda x: -cnt[x])
        ans = [0] * n
        idx = 0
        for code in ordered:
            for _ in range(cnt[code]):
                if idx >= n:
                    idx = 1
                ans[idx] = code
                idx += 2
        return ans

    def rearrangeBarcodes_heap(self, barcodes: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate classic max-heap: always append the most frequent remaining
        code different from last (or top two if needed).

        Algorithm:
        - heap of (-freq, code); pop top; if equals last and heap nonempty,
          pop second, push first back; append; decrement and push back

        Complexity: O(n log k) time, O(k) space.
        """
        cnt = Counter(barcodes)
        heap = [(-f, c) for c, f in cnt.items()]
        heapq.heapify(heap)
        ans = []
        prev_f, prev_c = 0, None
        while heap:
            f, c = heapq.heappop(heap)
            ans.append(c)
            if prev_f < 0:
                heapq.heappush(heap, (prev_f, prev_c))
            prev_f, prev_c = f + 1, c
        return ans
# @lc code=end
