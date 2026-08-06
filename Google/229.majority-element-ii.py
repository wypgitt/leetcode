"""
Approach: Boyer-Moore voting generalized for elements appearing more than n/3 times.
Data structure: at most two candidates and their counts are needed because there can be no more than two values with frequency greater than n/3.
Interview logic: pairs of different non-candidate elements can be canceled against the two candidates. A second pass verifies the surviving candidates because the first pass only finds possibilities.
Complexity: O(n) time, O(1) space.
Tests and edge cases: empty list returns []; one or two elements; candidate duplicates are filtered by verification.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def majorityElement(self, nums: List[int]) -> List[int]:
        cand1 = cand2 = None
        count1 = count2 = 0
        for num in nums:
            if num == cand1:
                count1 += 1
            elif num == cand2:
                count2 += 1
            elif count1 == 0:
                cand1, count1 = num, 1
            elif count2 == 0:
                cand2, count2 = num, 1
            else:
                count1 -= 1
                count2 -= 1
        return [cand for cand in (cand1, cand2) if cand is not None and nums.count(cand) > len(nums) // 3]
# @lc code=end
