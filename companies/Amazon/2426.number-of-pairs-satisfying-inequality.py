#
# @lc app=leetcode id=2426 lang=python3
#
# [2426] Number of Pairs Satisfying Inequality
#
# https://leetcode.com/problems/number-of-pairs-satisfying-inequality/description/
#
# algorithms
# Hard (47.73%)
# Likes:    586
# Dislikes: 11
# Total Accepted:    20.2K
# Total Submissions: 42.4K
# Testcase Example:  "[3,2,5]\n[2,2,1]\n1"
#
# You are given two 0-indexed integer arrays nums1 and nums2, each of size n,
# and an integer diff. Find the number of pairs (i, j) such that:
#
#
# 0 <= i < j <= n - 1 and
#
#
# nums1[i] - nums1[j] <= nums2[i] - nums2[j] + diff.
#
# Return the number of pairs that satisfy the conditions.
#
#
#
# Example 1:
#
# Input: nums1 = [3,2,5], nums2 = [2,2,1], diff = 1
# Output: 3
# Explanation:
# There are 3 pairs that satisfy the conditions:
# 1. i = 0, j = 1: 3 - 2 <= 2 - 2 + 1. Since i < j and 1 <= 1, this pair
# satisfies the conditions.
# 2. i = 0, j = 2: 3 - 5 <= 2 - 1 + 1. Since i < j and -2 <= 2, this pair
# satisfies the conditions.
# 3. i = 1, j = 2: 2 - 5 <= 2 - 1 + 1. Since i < j and -3 <= 2, this pair
# satisfies the conditions.
# Therefore, we return 3.
#
# Example 2:
#
# Input: nums1 = [3,-1], nums2 = [-2,2], diff = -1
# Output: 0
# Explanation:
# Since there does not exist any pair that satisfies the conditions, we return
# 0.
#
#
#
# Constraints:
#
#
# n == nums1.length == nums2.length
#
#
# 2 <= n <= 10^5
#
#
# -10^4 <= nums1[i], nums2[i] <= 10^4
#
#
# -10^4 <= diff <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def numberOfPairs(self, nums1: List[int], nums2: List[int], diff: int) -> int:
        """
        Interview explanation:
        Count pairs i < j with nums1[i]-nums1[j] <= nums2[i]-nums2[j]+diff, i.e.
        a[i] <= a[j]+diff for a[k]=nums1[k]-nums2[k].

        Algorithm:
        - Merge-sort based inversion-style counting on array a.

        Complexity: O(n log n) time, O(n) space.
        """
        a = [x - y for x, y in zip(nums1, nums2)]
        self.ans = 0

        def sort(arr: List[int]) -> List[int]:
            if len(arr) <= 1:
                return arr
            mid = len(arr) // 2
            left = sort(arr[:mid])
            right = sort(arr[mid:])
            j = 0
            for x in left:
                while j < len(right) and x > right[j] + diff:
                    j += 1
                self.ans += len(right) - j
            i = k = 0
            merged: List[int] = []
            while i < len(left) and k < len(right):
                if left[i] <= right[k]:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[k])
                    k += 1
            merged.extend(left[i:])
            merged.extend(right[k:])
            return merged

        sort(a)
        return self.ans

    def numberOfPairs_fenwick(self, nums1: List[int], nums2: List[int], diff: int) -> int:
        """
        Interview explanation:
        Alternate Fenwick/BIT after coordinate compression: for each a[j] from left
        to right, query count of prior a[i] <= a[j]+diff, then insert a[j].

        Algorithm:
        - Compress values including a[i]+diff thresholds; BIT frequencies.

        Complexity: O(n log n) time, O(n) space.
        """
        import bisect

        a = [x - y for x, y in zip(nums1, nums2)]
        vals = sorted(set(a + [x + diff for x in a]))
        idx = {v: i + 1 for i, v in enumerate(vals)}
        m = len(vals)
        bit = [0] * (m + 1)

        def add(i: int, d: int = 1) -> None:
            while i <= m:
                bit[i] += d
                i += i & -i

        def sum_(i: int) -> int:
            s = 0
            while i:
                s += bit[i]
                i -= i & -i
            return s

        ans = 0
        for x in a:
            pos = bisect.bisect_right(vals, x + diff)
            ans += sum_(pos)
            add(idx[x])
        return ans
# @lc code=end
