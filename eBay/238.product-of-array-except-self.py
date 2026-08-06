"""
Approach: Prefix products followed by suffix products.
Data structure: the output array first stores product of all elements to the left, then is multiplied by a running product of all elements to the right.
Interview logic: product except self = left product * right product. This avoids division and handles zeros naturally.
Complexity: O(n) time, O(1) extra space excluding the required output array.
Tests and edge cases: one zero makes only that index nonzero; two zeros make all outputs zero; negative signs multiply normally.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        ans = [1] * len(nums)
        prefix = 1
        for i, num in enumerate(nums):
            ans[i] = prefix
            prefix *= num
        suffix = 1
        for i in range(len(nums) - 1, -1, -1):
            ans[i] *= suffix
            suffix *= nums[i]
        return ans
# @lc code=end
