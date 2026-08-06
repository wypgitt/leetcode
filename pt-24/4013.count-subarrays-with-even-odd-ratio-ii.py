#
# @lc app=leetcode id=4013 lang=python3
#
# [4013] Count Subarrays With Even Odd Ratio II
#
# https://leetcode.com/problems/count-subarrays-with-even-odd-ratio-ii/description/
#
# algorithms
# Hard (38.64%)
# Likes:    43
# Dislikes: 2
# Total Accepted:    6K
# Total Submissions: 15.4K
# Testcase Example:  "[1,2,1,2]\n3\n2"
#
#
# You are given an integer array nums and two integers a and b.
#
# For a subarray, let:
#
# x be the number of even elements.
#
# y be the number of odd elements.
#
# The ratio of even to odd elements in a subarray is defined as x / y,
# where ratios are compared by their exact rational values.
#
# A subarray is considered valid if:
#
# y > 0, and
#
# x / y <= a / b.
#
# Return the number of valid subarrays in nums.
#
# Example 1:
#
# Input: nums = [1,2,1,2], a = 3, b = 2
#
# Output: 7
#
# Explanation:
#
# The following are the valid subarrays:
#
#                         Subarray
#                         Values
#                         Even Count
#                         Odd Count
#                         Ratio
#
#                         nums[0..0]
#                         [1]
#                         0
#                         1
#                         0 / 1
#
#                         nums[0..1]
#                         [1, 2]
#                         1
#                         1
#                         1 / 1
#
#                         nums[0..2]
#                         [1, 2, 1]
#                         1
#                         2
#                         1 / 2
#
#                         nums[0..3]
#                         [1, 2, 1, 2]
#                         2
#                         2
#                         2 / 2
#
#                         nums[1..2]
#                         [2, 1]
#                         1
#                         1
#                         1 / 1
#
#                         nums[2..2]
#                         [1]
#                         0
#                         1
#                         0 / 1
#
#                         nums[2..3]
#                         [1, 2]
#                         1
#                         1
#                         1 / 1
#
# Thus, the number of valid subarrays is 7.
#
# Example 2:
#
# Input: nums = [2,2,1], a = 2, b = 1
#
# Output: 3
#
# Explanation:
#
# The following are the valid subarrays:
#
#                         Subarray
#                         Values
#                         Even Count
#                         Odd Count
#                         Ratio
#
#                         nums[0..2]
#                         [2, 2, 1]
#                         2
#                         1
#                         2 / 1
#
#                         nums[1..2]
#                         [2, 1]
#                         1
#                         1
#                         1 / 1
#
#                         nums[2..2]
#                         [1]
#                         0
#                         1
#                         0 / 1
#
# Thus, the number of valid subarrays is 3.
#
# Example 3:
#
# Input: nums = [2,2,2], a = 1, b = 1
#
# Output: 0
#
# Explanation:
#
# Every subarray contains 0 odd numbers, so no subarray is valid.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= a, b <= 10^9​​​​​​​
#

# @lc code=start
from bisect import bisect_left


class BinaryIndexedTree:
    """Fenwick tree for prefix frequency queries."""

    __slots__ = ("n", "c")

    def __init__(self, n: int) -> None:
        self.n = n
        self.c = [0] * (n + 1)

    def update(self, x: int, delta: int) -> None:
        """
        Interview explanation:
        Fenwick point update: add delta at 1-based index x.

        Algorithm:
        - Walk x += x & -x updating nodes.

        Complexity: O(log n) time.
        """
        while x <= self.n:
            self.c[x] += delta
            x += x & -x

    def query(self, x: int) -> int:
        """
        Interview explanation:
        Fenwick prefix sum on [1..x].

        Algorithm:
        - Walk x -= x & -x accumulating.

        Complexity: O(log n) time.
        """
        s = 0
        while x:
            s += self.c[x]
            x -= x & -x
        return s


class Solution:
    def countRatioSubarrays(self, nums: list[int], a: int, b: int) -> int:
        """
        Interview explanation:
        Same ratio condition as I, but n ≤ 1e5. Map even→−b, odd→+a so a
        subarray is valid iff its prefix-delta is ≥ 0 (all-even ⇒ negative).

        Algorithm:
        - Build prefix s; compress values.
        - Sweep left→right: for each s[r], BIT counts prior s[l] ≤ s[r].

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        s = [0] * (n + 1)
        for i, x in enumerate(nums):
            s[i + 1] = s[i] + (a if x % 2 else -b)

        st = sorted(set(s))
        bit = BinaryIndexedTree(len(st) + 1)
        ans = 0
        for v in s:
            x = bisect_left(st, v) + 1
            ans += bit.query(x)
            bit.update(x, 1)
        return ans
# @lc code=end
