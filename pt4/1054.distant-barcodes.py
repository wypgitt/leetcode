#
# @lc app=leetcode id=1054 lang=python3
#
# [1054] Distant Barcodes
#
# https://leetcode.com/problems/distant-barcodes/description/
#
# algorithms
# Medium (48.90%)
# Likes:    1355
# Dislikes: 52
# Total Accepted:    58K
# Total Submissions: 118.5K
# Testcase Example:  '[1,1,1,2,2,2]'
#
# In a warehouse, there is a row of barcodes, where the i^th barcode is
# barcodes[i].
# 
# Rearrange the barcodes so that no two adjacent barcodes are equal. You may
# return any answer, and it is guaranteed an answer exists.
# 
# 
# Example 1:
# Input: barcodes = [1,1,1,2,2,2]
# Output: [2,1,2,1,2,1]
# Example 2:
# Input: barcodes = [1,1,1,1,2,2,3,3]
# Output: [1,3,1,3,1,2,1,2]
# 
# 
# Constraints:
# 
# 
# 1 <= barcodes.length <= 10000
# 1 <= barcodes[i] <= 10000
# 
# 
#

# @lc code=start
from collections import Counter
from heapq import heapify, heappop, heappush
from typing import List


class Solution:
    def rearrangeBarcodes(self, barcodes: List[int]) -> List[int]:
        heap = [(-count, barcode) for barcode, count in Counter(barcodes).items()]
        heapify(heap)

        result = []
        previous_count = 0
        previous_barcode = 0

        while heap:
            count, barcode = heappop(heap)
            result.append(barcode)
            count += 1

            if previous_count < 0:
                heappush(heap, (previous_count, previous_barcode))

            previous_count = count
            previous_barcode = barcode

        return result
# @lc code=end

"""
Interview Explanation

Core idea:
Always place the barcode with the largest remaining count that is not equal to
the barcode placed immediately before it. Holding the previous barcode out of
the heap for one step enforces the adjacency rule.

Algorithm:
1. Count barcode frequencies.
2. Store them in a max heap using negative counts.
3. Repeatedly pop the most frequent currently allowed barcode and append it.
4. Decrease its count.
5. Push the previous barcode back only after a different barcode has been
   placed.

Data structure choice:
A max heap gives quick access to the most frequent remaining barcode. The
single "previous" slot temporarily blocks the last placed value from being
chosen again immediately.

Correctness:
The algorithm never places the same barcode twice in a row because the last
placed barcode is not in the heap during the next selection. Choosing the most
frequent available barcode is safe because a valid answer is guaranteed, and
using high-frequency values early prevents them from being stranded at the end.

Complexity:
Let n be the number of barcodes and k the number of distinct values. Time is
O(n log k), and space is O(k) besides the result.

Tests and edge cases:
- One barcode: returns it.
- Two equally frequent barcodes alternate.
- One dominant barcode, such as [1,1,1,1,2,2,3,3], is spread out.
- The returned order may differ from examples; any valid arrangement is fine.
"""
