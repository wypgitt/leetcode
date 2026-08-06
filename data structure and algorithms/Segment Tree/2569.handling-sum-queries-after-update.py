#
# @lc app=leetcode id=2569 lang=python3
#
# [2569] Handling Sum Queries After Update
#
# https://leetcode.com/problems/handling-sum-queries-after-update/description/
#
# algorithms
# Hard (31.67%)
# Likes:    205
# Dislikes: 25
# Total Accepted:    8.5K
# Total Submissions: 27K
# Testcase Example:  "[1,0,1]\n[0,0,0]\n[[1,1,1],[2,1,0],[3,0,0]]"
#
# You are given two 0-indexed arrays nums1 and nums2 and a 2D array queries of
# queries. There are three types of queries:
#
#
# For a query of type 1, queries[i] = [1, l, r]. Flip the values from 0 to 1 and
# from 1 to 0 in nums1 from index l to index r. Both l and r are 0-indexed.
#
#
# For a query of type 2, queries[i] = [2, p, 0]. For every index 0 <= i < n,
# set nums2[i] = nums2[i] + nums1[i] * p.
#
#
# For a query of type 3, queries[i] = [3, 0, 0]. Find the sum of the elements in
# nums2.
#
# Return an array containing all the answers to the third type queries.
#
#
#
# Example 1:
#
# Input: nums1 = [1,0,1], nums2 = [0,0,0], queries = [[1,1,1],[2,1,0],[3,0,0]]
# Output: [3]
# Explanation: After the first query nums1 becomes [1,1,1]. After the second
# query, nums2 becomes [1,1,1], so the answer to the third query is 3. Thus, [3]
# is returned.
#
# Example 2:
#
# Input: nums1 = [1], nums2 = [5], queries = [[2,0,0],[3,0,0]]
# Output: [5]
# Explanation: After the first query, nums2 remains [5], so the answer to the
# second query is 5. Thus, [5] is returned.
#
#
#
# Constraints:
#
#
# 1 <= nums1.length,nums2.length <= 10^5
#
#
# nums1.length = nums2.length
#
#
# 1 <= queries.length <= 10^5
#
#
# queries[i].length = 3
#
#
# 0 <= l <= r <= nums1.length - 1
#
#
# 0 <= p <= 10^6
#
#
# 0 <= nums1[i] <= 1
#
#
# 0 <= nums2[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def handleQuery(self, nums1: List[int], nums2: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Process queries: flip nums1[l..r], add sum(nums1)*p to all of nums2 conceptually
        via a maintained total, and record sum(nums2) on type-3 queries. Use a segment
        tree on nums1 for range flips and range ones-count.

        Algorithm:
        - Segment tree with lazy XOR flip; store count of ones in each node.
        - total = sum(nums2); on type 2: total += ones * p; on type 3 append total.

        Complexity: O((n+q) log n) time, O(n) space.
        """
        n = len(nums1)
        ones = [0] * (4 * n)
        lazy = [0] * (4 * n)

        def build(idx, l, r):
            if l == r:
                ones[idx] = nums1[l]
                return
            m = (l + r) // 2
            build(idx * 2, l, m)
            build(idx * 2 + 1, m + 1, r)
            ones[idx] = ones[idx * 2] + ones[idx * 2 + 1]

        def apply(idx, l, r):
            ones[idx] = (r - l + 1) - ones[idx]
            lazy[idx] ^= 1

        def push(idx, l, r):
            if lazy[idx] and l != r:
                m = (l + r) // 2
                apply(idx * 2, l, m)
                apply(idx * 2 + 1, m + 1, r)
                lazy[idx] = 0

        def update(idx, l, r, ql, qr):
            if qr < l or r < ql:
                return
            if ql <= l and r <= qr:
                apply(idx, l, r)
                return
            push(idx, l, r)
            m = (l + r) // 2
            update(idx * 2, l, m, ql, qr)
            update(idx * 2 + 1, m + 1, r, ql, qr)
            ones[idx] = ones[idx * 2] + ones[idx * 2 + 1]

        build(1, 0, n - 1)
        total = sum(nums2)
        ans = []
        for typ, a, b in queries:
            if typ == 1:
                update(1, 0, n - 1, a, b)
            elif typ == 2:
                total += ones[1] * a
            else:
                ans.append(total)
        return ans
# @lc code=end
