#
# @lc app=leetcode id=307 lang=python3
#
# [307] Range Sum Query - Mutable
#
# https://leetcode.com/problems/range-sum-query-mutable/description/
#
# algorithms
# Medium (43.52%)
# Likes:    5215
# Dislikes: 274
# Total Accepted:    363K
# Total Submissions: 835K
# Testcase Example:  "[\"NumArray\",\"sumRange\",\"update\",\"sumRange\"]"
#
# Given an integer array nums, handle multiple queries of the following types:
#
# Update the value of an element in nums.
#
# Calculate the sum of the elements of nums between indices left and right
# inclusive where left <= right.
#
# Implement the NumArray class:
#
# NumArray(int[] nums) Initializes the object with the integer array nums.
#
# void update(int index, int val) Updates the value of nums[index] to be val.
#
# int sumRange(int left, int right) Returns the sum of the elements of nums
# between indices left and right inclusive (i.e. nums[left] + nums[left + 1] +
# ... + nums[right]).
#
# Example 1:
#
# Input
# ["NumArray", "sumRange", "update", "sumRange"]
# [[[1, 3, 5]], [0, 2], [1, 2], [0, 2]]
# Output
# [null, 9, null, 8]
#
# Explanation
# NumArray numArray = new NumArray([1, 3, 5]);
# numArray.sumRange(0, 2); // return 1 + 3 + 5 = 9
# numArray.update(1, 2); // nums = [1, 2, 5]
# numArray.sumRange(0, 2); // return 1 + 2 + 5 = 8
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# -100 <= nums[i] <= 100
#
# 0 <= index < nums.length
#
# -100 <= val <= 100
#
# 0 <= left <= right < nums.length
#
# At most 3 * 10^4 calls will be made to update and sumRange.
#

# @lc code=start
from typing import List


class NumArray:
    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Fenwick / Binary Indexed Tree supports point updates and prefix sums
        in O(log n). Range sum = prefix(right+1) - prefix(left).

        Algorithm:
        - Copy nums; bit array of size n+1; for each value, _add(i+1, v).

        Complexity: O(n log n) build, O(log n) update/query, O(n) space.
        """
        self.n = len(nums)
        self.nums = nums[:]
        self.bit = [0] * (self.n + 1)
        for i, v in enumerate(nums):
            self._add(i + 1, v)

    def _add(self, i: int, delta: int) -> None:
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def _prefix(self, i: int) -> int:
        s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s

    def update(self, index: int, val: int) -> None:
        """
        Interview explanation:
        Point update via Fenwick: apply delta = val - old at 1-based index.

        Algorithm:
        - Compute delta; store nums[index]=val; _add(index+1, delta).

        Complexity: O(log n) time, O(1) extra space.
        """
        delta = val - self.nums[index]
        self.nums[index] = val
        self._add(index + 1, delta)

    def sumRange(self, left: int, right: int) -> int:
        """
        Interview explanation:
        Range sum as difference of two Fenwick prefix sums.

        Algorithm:
        - Return _prefix(right+1) - _prefix(left).

        Complexity: O(log n) time, O(1) space.
        """
        return self._prefix(right + 1) - self._prefix(left)


class NumArraySegmentTree:
    """
    Interview explanation:
    Alternate: iterative segment tree for range sum + point update. Leaves at
    [n..2n); parents store child sums. Update walks to root; query covers
    [left,right] by taking O(log n) disjoint nodes.
    """

    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Build a flat segment tree: copy nums into the leaf half, then fill
        parents bottom-up as sums of children.

        Algorithm:
        - tree[n+i] = nums[i]; for i = n-1..1: tree[i] = tree[2i]+tree[2i+1].

        Complexity: O(n) build, O(n) space.
        """
        self.n = len(nums)
        self.tree = [0] * (2 * self.n)
        for i, v in enumerate(nums):
            self.tree[self.n + i] = v
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index: int, val: int) -> None:
        """
        Interview explanation:
        Set leaf to val and recompute every ancestor sum up to the root.

        Algorithm:
        - i = index+n; tree[i]=val; while i>1: i//=2; tree[i]=children sum.

        Complexity: O(log n) time, O(1) space.
        """
        i = index + self.n
        self.tree[i] = val
        while i > 1:
            i //= 2
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def sumRange(self, left: int, right: int) -> int:
        """
        Interview explanation:
        Cover [left,right] with O(log n) segment-tree nodes via the classic
        iterative left/right walk.

        Algorithm:
        - Map to leaf indices; while l<=r, add odd l / even r nodes, then /=2.

        Complexity: O(log n) time, O(1) space.
        """
        l, r = left + self.n, right + self.n
        s = 0
        while l <= r:
            if l % 2 == 1:
                s += self.tree[l]
                l += 1
            if r % 2 == 0:
                s += self.tree[r]
                r -= 1
            l //= 2
            r //= 2
        return s


# Your NumArray object will be instantiated and called as such:
# obj = NumArray(nums)
# obj.update(index,val)
# param_2 = obj.sumRange(left,right)
# @lc code=end

