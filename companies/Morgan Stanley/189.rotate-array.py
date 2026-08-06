"""
Approach: Three in-place reversals.
Data structure: two-pointer swaps mutate the array using O(1) space.
Interview logic: reversing the whole array puts the last k elements first but reversed; reversing the first k and remaining n-k sections restores internal order.
Complexity: O(n) time, O(1) space.
Tests and edge cases: k can exceed n and is reduced modulo n; k = 0 leaves array unchanged; length 1 is safe.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        n = len(nums)
        k %= n
        def rev(left: int, right: int) -> None:
            while left < right:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
                right -= 1
        rev(0, n - 1)
        rev(0, k - 1)
        rev(k, n - 1)
# @lc code=end
