#
# @lc app=leetcode id=3948 lang=python3
#
# [3948] Lexicographically Maximum MEX Array
#
# https://leetcode.com/problems/lexicographically-maximum-mex-array/description/
#
# algorithms
# Hard (57.22%)
# Likes:    50
# Dislikes: 4
# Total Accepted:    7.9K
# Total Submissions: 13.9K
# Testcase Example:  "[0,1,0]"
#
#
# You are given an integer array nums.
#
# You want to construct an array result by repeatedly performing the
# following operation until nums becomes empty:
#
# Choose an integer k such that 1 <= k <= len(nums).
#
# Compute the MEX of the first k elements of nums.
#
# Append this MEX to result.
#
# Remove the first k elements from nums.
#
# Return the lexicographically maximum array result that can be obtained
# after performing the operations.
#
# The MEX of an array is the smallest non-negative integer not present in
# the array.
#
# An array a is lexicographically greater than an array b if in the first
# position where a and b differ, array a has an element that is greater
# than the corresponding element in b. If the first min(a.length,
# b.length) elements do not differ, then the longer array is the
# lexicographically greater one.
#
# Example 1:
#
# Input: nums = [0,1,0]
#
# Output: [2,1]
#
# Explanation:
#
# Take the first k = 2 elements [0, 1] which has MEX = 2. Current result =
# [2].
#
# Remaining array [0] has MEX = 1. Thus, the final result = [2, 1].
#
# Example 2:
#
# Input: nums = [1,0,2]
#
# Output: [3]
#
# Explanation:
#
# Take the first k = 3 elements [1, 0, 2] which has MEX = 3.
#
# nums is now empty. Thus, the final result = [3].
#
# Example 3:
#
# Input: nums = [3,1]
#
# Output: [0,0]
#
# Explanation:​​​​​​​
#
# Take k = 1, first element [3] has MEX = 0. Current result = [0].
#
# Remaining array [1] has MEX = 0. Thus, the final result = [0, 0].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maximumMEX(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Lexicographic maximum means each prefix MEX should be as large as
        possible, i.e. the MEX of the remaining suffix, taken with the shortest
        prefix that realizes it (classic "Meximum Array").

        Algorithm:
        - Track global missing values of the remaining suffix.
        - Repeatedly append current suffix MEX; walk the shortest prefix that
          contains every value in 0..mex-1, dropping those from the suffix.

        Complexity: O(n) time amortized, O(n) space.
        """
        n = len(nums)
        freq = [0] * (n + 2)
        for x in nums:
            if x <= n:
                freq[x] += 1
        missing = set(x for x in range(n + 2) if freq[x] == 0)
        result = []
        seen = [0] * (n + 2)
        timer = 0
        i = 0

        def remove(val: int) -> None:
            if val <= n:
                freq[val] -= 1
                if freq[val] == 0:
                    missing.add(val)

        while i < n:
            mex = min(missing)
            if mex == 0:
                result.append(0)
                remove(nums[i])
                i += 1
                continue
            result.append(mex)
            timer += 1
            need = mex
            while i < n and need > 0:
                x = nums[i]
                remove(x)
                if x < mex and seen[x] != timer:
                    seen[x] = timer
                    need -= 1
                i += 1
        return result
# @lc code=end
