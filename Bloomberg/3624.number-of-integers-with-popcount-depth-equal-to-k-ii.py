#
# @lc app=leetcode id=3624 lang=python3
#
# [3624] Number of Integers With Popcount-Depth Equal to K II
#
# https://leetcode.com/problems/number-of-integers-with-popcount-depth-equal-to-k-ii/description/
#
# algorithms
# Hard (58.49%)
# Likes:    36
# Dislikes: 9
# Total Accepted:    20.6K
# Total Submissions: 35.2K
# Testcase Example:  "[2,4]\n[[1,0,1,1],[2,1,1],[1,0,1,0]]"
#
#
# You are given an integer array nums.
#
# For any positive integer x, define the following sequence:
#
# p_0 = x
#
# p_i+1 = popcount(p_i) for all i >= 0, where popcount(y) is the number of
# set bits (1's) in the binary representation of y.
#
# This sequence will eventually reach the value 1.
#
# The popcount-depth of x is defined as the smallest integer d >= 0 such
# that p_d = 1.
#
# For example, if x = 7 (binary representation "111"). Then, the sequence
# is: 7 → 3 → 2 → 1, so the popcount-depth of 7 is 3.
#
# You are also given a 2D integer array queries, where each queries[i] is
# either:
#
# [1, l, r, k] - Determine the number of indices j such that l <= j <= r
# and the popcount-depth of nums[j] is equal to k.
#
# [2, idx, val] - Update nums[idx] to val.
#
# Return an integer array answer, where answer[i] is the number of indices
# for the i^th query of type [1, l, r, k].
#
# Example 1:
#
# Input: nums = [2,4], queries = [[1,0,1,1],[2,1,1],[1,0,1,0]]
#
# Output: [2,1]
#
# Explanation:
#
#                         i
#                         queries[i]
#                         nums
#                         binary(nums)
#                         popcount-
#
#                         depth
#                         [l, r]
#                         k
#                         Valid
#
#                         nums[j]
#                         updated
#
#                         nums
#                         Answer
#
#                         0
#                         [1,0,1,1]
#                         [2,4]
#                         [10, 100]
#                         [1, 1]
#                         [0, 1]
#                         1
#                         [0, 1]
#                         —
#                         2
#
#                         1
#                         [2,1,1]
#                         [2,4]
#                         [10, 100]
#                         [1, 1]
#                         —
#                         —
#                         —
#                         [2,1]
#                         —
#
#                         2
#                         [1,0,1,0]
#                         [2,1]
#                         [10, 1]
#                         [1, 0]
#                         [0, 1]
#                         0
#                         [1]
#                         —
#                         1
#
# Thus, the final answer is [2, 1].
#
# Example 2:
#
# Input: nums = [3,5,6], queries = [[1,0,2,2],[2,1,4],[1,1,2,1],[1,0,1,0]]
#
# Output: [3,1,0]
#
# Explanation:
#
#                         i
#                         queries[i]
#                         nums
#                         binary(nums)
#                         popcount-
#
#                         depth
#                         [l, r]
#                         k
#                         Valid
#
#                         nums[j]
#                         updated
#
#                         nums
#                         Answer
#
#                         0
#                         [1,0,2,2]
#                         [3, 5, 6]
#                         [11, 101, 110]
#                         [2, 2, 2]
#                         [0, 2]
#                         2
#                         [0, 1, 2]
#                         —
#                         3
#
#                         1
#                         [2,1,4]
#                         [3, 5, 6]
#                         [11, 101, 110]
#                         [2, 2, 2]
#                         —
#                         —
#                         —
#                         [3, 4, 6]
#                         —
#
#                         2
#                         [1,1,2,1]
#                         [3, 4, 6]
#                         [11, 100, 110]
#                         [2, 1, 2]
#                         [1, 2]
#                         1
#                         [1]
#                         —
#                         1
#
#                         3
#                         [1,0,1,0]
#                         [3, 4, 6]
#                         [11, 100, 110]
#                         [2, 1, 2]
#                         [0, 1]
#                         0
#                         []
#                         —
#                         0
#
# Thus, the final answer is [3, 1, 0].
#
# Example 3:
#
# Input: nums = [1,2], queries = [[1,0,1,1],[2,0,3],[1,0,0,1],[1,0,0,2]]
#
# Output: [1,0,1]
#
# Explanation:
#
#                         i
#                         queries[i]
#                         nums
#                         binary(nums)
#                         popcount-
#
#                         depth
#                         [l, r]
#                         k
#                         Valid
#
#                         nums[j]
#                         updated
#
#                         nums
#                         Answer
#
#                         0
#                         [1,0,1,1]
#                         [1, 2]
#                         [1, 10]
#                         [0, 1]
#                         [0, 1]
#                         1
#                         [1]
#                         —
#                         1
#
#                         1
#                         [2,0,3]
#                         [1, 2]
#                         [1, 10]
#                         [0, 1]
#                         —
#                         —
#                         —
#                         [3, 2]
#
#                         2
#                         [1,0,0,1]
#                         [3, 2]
#                         [11, 10]
#                         [2, 1]
#                         [0, 0]
#                         1
#                         []
#                         —
#                         0
#
#                         3
#                         [1,0,0,2]
#                         [3, 2]
#                         [11, 10]
#                         [2, 1]
#                         [0, 0]
#                         2
#                         [0]
#                         —
#                         1
#
# Thus, the final answer is [1, 0, 1].
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^15
#
# 1 <= queries.length <= 10^5
#
# queries[i].length == 3 or 4
#
# queries[i] == [1, l, r, k] or,
#
# queries[i] == [2, idx, val]
#
# 0 <= l <= r <= n - 1
#
# 0 <= k <= 5
#
# 0 <= idx <= n - 1
#
# 1 <= val <= 10^15
#

# @lc code=start

from typing import List


class _BIT:
    """Fenwick tree for point updates and prefix sums (0-indexed)."""

    def __init__(self, n: int):
        self.bit = [0] * (n + 1)

    def add(self, i: int, val: int) -> None:
        """
        Interview explanation:
        Fenwick point update: add val at 0-based index i.

        Algorithm:
        - Convert to 1-based; walk i += i & -i updating nodes.

        Complexity: O(log n) time.
        """
        i += 1
        while i < len(self.bit):
            self.bit[i] += val
            i += i & -i

    def query(self, i: int) -> int:
        """
        Interview explanation:
        Fenwick prefix sum on indices [0..i] (0-based inclusive).

        Algorithm:
        - Convert to 1-based; walk i -= i & -i accumulating.

        Complexity: O(log n) time.
        """
        i += 1
        ret = 0
        while i > 0:
            ret += self.bit[i]
            i -= i & -i
        return ret


class Solution:
    def popcountDepth(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Maintain popcount-depth of each nums[i] under range-count and point
        update queries. Depth is in 0..5, so keep one Fenwick tree per depth.

        Algorithm:
        - depth(x)=0 if x==1 else 1+D[popcount(x)] with D precomputed.
        - For type-1 [1,l,r,k]: answer bits[k].prefix(r)-bits[k].prefix(l-1).
        - For type-2 [2,idx,val]: move idx from old depth to new depth in BITs.

        Complexity: O((n+q) log n) time, O(n) space.
        """
        n = len(nums)
        bits = [_BIT(n) for _ in range(6)]
        for i, x in enumerate(nums):
            bits[self._depth(x)].add(i, 1)

        ans = []
        for q in queries:
            if q[0] == 1:
                _, l, r, k = q
                ans.append(bits[k].query(r) - bits[k].query(l - 1))
            else:
                _, idx, val = q
                old_d = self._depth(nums[idx])
                new_d = self._depth(val)
                if old_d != new_d:
                    bits[old_d].add(idx, -1)
                    bits[new_d].add(idx, 1)
                nums[idx] = val
        return ans

    def _depth(self, x: int) -> int:
        return 0 if x == 1 else self._D[bin(x).count("1")] + 1


def _init_depth():
    max_bits = (10**15).bit_length()
    depth = [0] * (max_bits + 1)
    for i in range(2, max_bits + 1):
        depth[i] = depth[bin(i).count("1")] + 1
    return depth


Solution._D = _init_depth()
# @lc code=end

