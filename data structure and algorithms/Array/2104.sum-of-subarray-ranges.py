#
# @lc app=leetcode id=2104 lang=python3
#
# [2104] Sum of Subarray Ranges
#
# https://leetcode.com/problems/sum-of-subarray-ranges/description/
#
# algorithms
# Medium (61.71%)
# Likes:    3086
# Dislikes: 148
# Total Accepted:    251K
# Total Submissions: 406.7K
# Testcase Example:  "[1,2,3]"
#
# You are given an integer array nums. The range of a subarray of nums is the
# difference between the largest and smallest element in the subarray.
#
# Return the sum of all subarray ranges of nums.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3]
# Output: 4
# Explanation: The 6 subarrays of nums are the following:
# [1], range = largest - smallest = 1 - 1 = 0
# [2], range = 2 - 2 = 0
# [3], range = 3 - 3 = 0
# [1,2], range = 2 - 1 = 1
# [2,3], range = 3 - 2 = 1
# [1,2,3], range = 3 - 1 = 2
# So the sum of all ranges is 0 + 0 + 0 + 1 + 1 + 2 = 4.
#
# Example 2:
#
# Input: nums = [1,3,3]
# Output: 4
# Explanation: The 6 subarrays of nums are the following:
# [1], range = largest - smallest = 1 - 1 = 0
# [3], range = 3 - 3 = 0
# [3], range = 3 - 3 = 0
# [1,3], range = 3 - 1 = 2
# [3,3], range = 3 - 3 = 0
# [1,3,3], range = 3 - 1 = 2
# So the sum of all ranges is 0 + 0 + 0 + 2 + 0 + 2 = 4.
#
# Example 3:
#
# Input: nums = [4,-2,-3,4,1]
# Output: 59
# Explanation: The sum of all subarray ranges of nums is 59.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# -10^9 <= nums[i] <= 10^9
#
#
#
# Follow-up: Could you find a solution with O(n) time complexity?
#


# @lc code=start
from typing import List


class Solution:
    def subArrayRanges(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum of (max-min) over all subarrays. Equivalent to sum of subarray
        maxima minus sum of subarray minima.

        Algorithm:
        - For each element, count subarrays where it is strict max / min via
          previous/next less/greater bounds; accumulate contrib.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)

        def contrib(op) -> int:
            # op True => contribution as maximum, else as minimum
            left = [0] * n
            right = [0] * n
            st = []
            for i in range(n):
                while st and (nums[st[-1]] < nums[i] if op else nums[st[-1]] > nums[i]):
                    st.pop()
                left[i] = i - (st[-1] if st else -1)
                st.append(i)
            st.clear()
            for i in range(n - 1, -1, -1):
                while st and (nums[st[-1]] <= nums[i] if op else nums[st[-1]] >= nums[i]):
                    st.pop()
                right[i] = (st[-1] if st else n) - i
                st.append(i)
            return sum(nums[i] * left[i] * right[i] for i in range(n))

        return contrib(True) - contrib(False)


# @lc code=end

