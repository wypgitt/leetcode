#
# @lc app=leetcode id=3943 lang=python3
#
# [3943] Number of Pairs After Increment
#
# https://leetcode.com/problems/number-of-pairs-after-increment/description/
#
# algorithms
# Hard (21.34%)
# Likes:    56
# Dislikes: 2
# Total Accepted:    5.7K
# Total Submissions: 26.8K
# Testcase Example:  "[1,2]\n[3,4]\n[[2,5],[1,0,0,2],[2,5]]"
#
#
# You are given two integer arrays nums1 and nums2, and a 2D integer array
# queries.
#
# Each queries[i] is one of the following types:
#
# [1, x, y, val] – Add val to every element in nums2[x..y].
#
# [2, tot] – Compute the number of pairs (j, k) such that nums1[j] +
# nums2[k] == tot.
#
# Return an integer array answer, where answer[j] is the number of pairs
# for the j^th query of type 2.
#
# Example 1:
#
# Input: nums1 = [1,2], nums2 = [3,4], queries = [[2,5],[1,0,0,2],[2,5]]
#
# Output: [2,1]
#
# Explanation:
#
# queries[0] = [2, 5]: Valid pairs are nums1[0] + nums2[1] = 1 + 4 = 5 and
# nums1[1] + nums2[0] = 2 + 3 = 5.
#
# queries[1] = [1, 0, 0, 2]: Add 2 to nums2[0], resulting in nums2 = [5,
# 4].
#
# queries[2] = [2, 5]: Valid pair is nums1[0] + nums2[1] = 1 + 4 = 5.
#
# Thus, the answer = [2, 1].
#
# Example 2:
#
# Input: nums1 = [1,1], nums2 = [2,2,3], queries = [[2,4],[1,0,1,1],[2,4]]
#
# Output: [2,6]
#
# Explanation:
#
# queries[0] = [2, 4]: Valid pairs are nums1[0] + nums2[2] = 1 + 3 and
# nums1[1] + nums2[2] = 1 + 3.
#
# queries[1] = [1, 0, 1, 1]: Add 1 to nums2[0] and nums2[1], resulting in
# nums2 = [3, 3, 3].
#
# queries[2] = [2, 4]: Every element of nums1 = [1, 1] pairs with every
# element of nums2 = [3, 3, 3] as 1 + 3 = 4. That gives 2 × 3 = 6 pairs in
# total.
#
# Thus, the answer = [2, 6].
#
# Example 3:
#
# Input: nums1 = [2,5,8,4], nums2 = [1,3,8], queries =
# [[2,9],[1,1,2,1],[2,10]]
#
# Output: [1,0]
#
# Explanation:
#
# queries[0] = [2, 9]: Only valid pair is nums1[2] + nums2[0] = 8 + 1 = 9.
#
# queries[1] = [1, 1, 2, 1]: Add 1 to nums2[1] and nums2[2], resulting
# in​​​​​​​ nums2 = [1, 4, 9].
#
# queries[2] = [2, 10]: No pair sums to 10.
#
# Thus, the answer = [1, 0].
#
# Constraints:
#
# 1 <= nums1.length <= 5
#
# 1 <= nums2.length <= 5 * 10^4
#
# 1 <= nums1[i], nums2[i] <= 10^5
#
# 1 <= queries.length <= 5 * 10^4
#
# queries[i].length == 2 or 4
#
# queries[i] == [1, x, y, val], or
#
# queries[i] == [2, tot]
#
# 0 <= x <= y < nums2.length
#
# 1 <= val <= 10^5
#
# 1 <= tot <= 10^9​​​​​​​
#

# @lc code=start
from collections import defaultdict
from math import isqrt


class Solution:
    def numberOfPairs(self, nums1: list[int], nums2: list[int], queries: list[list[int]]) -> list[int]:
        """
        Interview explanation:
        nums1 is tiny (≤5); nums2 is large with range adds and pair-count
        queries. Maintain frequency maps per sqrt block with lazy adds.

        Algorithm:
        - Split nums2 into blocks of size ~sqrt(n); store value freqs and lazy.
        - Type-1: update partial blocks in place; full blocks bump lazy.
        - Type-2: for each a in nums1 and each block, look up tot-a-lazy.

        Complexity: O((n+q)·√n·|nums1|) time, O(n) space.
        """
        n = len(nums2)
        B = max(1, isqrt(n))
        nb = (n + B - 1) // B
        arr = nums2[:]
        freq = [defaultdict(int) for _ in range(nb)]
        lazy = [0] * nb
        for i, v in enumerate(arr):
            freq[i // B][v] += 1

        ans = []
        for q in queries:
            if q[0] == 1:
                _, L, R, val = q
                i = L
                while i <= R:
                    b = i // B
                    bl, br = b * B, min(n, (b + 1) * B) - 1
                    if i == bl and br <= R:
                        lazy[b] += val
                        i = br + 1
                    else:
                        end = min(br, R)
                        while i <= end:
                            old = arr[i]
                            freq[b][old] -= 1
                            if freq[b][old] == 0:
                                del freq[b][old]
                            arr[i] = old + val
                            freq[b][arr[i]] += 1
                            i += 1
            else:
                tot = q[1]
                c = 0
                for a in nums1:
                    for b in range(nb):
                        need = tot - a - lazy[b]
                        c += freq[b].get(need, 0)
                ans.append(c)
        return ans
# @lc code=end
