#
# @lc app=leetcode id=3072 lang=python3
#
# [3072] Distribute Elements Into Two Arrays II
#
# https://leetcode.com/problems/distribute-elements-into-two-arrays-ii/description/
#
# algorithms
# Hard (31.15%)
# Likes:    162
# Dislikes: 14
# Total Accepted:    14.9K
# Total Submissions: 47.7K
# Testcase Example:  "[2,1,3,3]"
#
#
# You are given a 1-indexed array of integers nums of length n.
#
# We define a function greaterCount such that greaterCount(arr, val)
# returns the number of elements in arr that are strictly greater than
# val.
#
# You need to distribute all the elements of nums between two arrays arr1
# and arr2 using n operations. In the first operation, append nums[1] to
# arr1. In the second operation, append nums[2] to arr2. Afterwards, in
# the i^th operation:
#
# If greaterCount(arr1, nums[i]) > greaterCount(arr2, nums[i]), append
# nums[i] to arr1.
#
# If greaterCount(arr1, nums[i]) < greaterCount(arr2, nums[i]), append
# nums[i] to arr2.
#
# If greaterCount(arr1, nums[i]) == greaterCount(arr2, nums[i]), append
# nums[i] to the array with a lesser number of elements.
#
# If there is still a tie, append nums[i] to arr1.
#
# The array result is formed by concatenating the arrays arr1 and arr2.
# For example, if arr1 == [1,2,3] and arr2 == [4,5,6], then result =
# [1,2,3,4,5,6].
#
# Return the integer array result.
#
# Example 1:
#
# Input: nums = [2,1,3,3]
# Output: [2,3,1,3]
# Explanation: After the first 2 operations, arr1 = [2] and arr2 = [1].
# In the 3^rd operation, the number of elements greater than 3 is zero in
# both arrays. Also, the lengths are equal, hence, append nums[3] to arr1.
# In the 4^th operation, the number of elements greater than 3 is zero in
# both arrays. As the length of arr2 is lesser, hence, append nums[4] to
# arr2.
# After 4 operations, arr1 = [2,3] and arr2 = [1,3].
# Hence, the array result formed by concatenation is [2,3,1,3].
#
# Example 2:
#
# Input: nums = [5,14,3,1,2]
# Output: [5,3,1,2,14]
# Explanation: After the first 2 operations, arr1 = [5] and arr2 = [14].
# In the 3^rd operation, the number of elements greater than 3 is one in
# both arrays. Also, the lengths are equal, hence, append nums[3] to arr1.
# In the 4^th operation, the number of elements greater than 1 is greater
# in arr1 than arr2 (2 > 1). Hence, append nums[4] to arr1.
# In the 5^th operation, the number of elements greater than 2 is greater
# in arr1 than arr2 (2 > 1). Hence, append nums[5] to arr1.
# After 5 operations, arr1 = [5,3,1,2] and arr2 = [14].
# Hence, the array result formed by concatenation is [5,3,1,2,14].
#
# Example 3:
#
# Input: nums = [3,3,3,3]
# Output: [3,3,3,3]
# Explanation: At the end of 4 operations, arr1 = [3,3] and arr2 = [3,3].
# Hence, the array result formed by concatenation is [3,3,3,3].
#
# Constraints:
#
# 3 <= n <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def resultArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Distribute nums into arr1/arr2 using greaterCount comparisons (n up to
        1e5). Maintain two sorted multisets via Fenwick trees on compressed ranks.

        Algorithm:
        - Coordinate-compress values. Each BIT stores frequencies; greaterCount
          = total - prefix(rank(val)). Append per problem tie-break rules.

        Complexity: O(n log n) time, O(n) space.
        """
        class BIT:
            def __init__(self, n: int):
                self.n = n
                self.t = [0] * (n + 1)

            def add(self, i: int, v: int = 1) -> None:
                while i <= self.n:
                    self.t[i] += v
                    i += i & -i

            def sum(self, i: int) -> int:
                s = 0
                while i > 0:
                    s += self.t[i]
                    i -= i & -i
                return s

            def greater(self, i: int) -> int:
                # count of ranks > i
                return self.sum(self.n) - self.sum(i)

        vals = sorted(set(nums))
        rank = {v: i + 1 for i, v in enumerate(vals)}
        m = len(vals)
        bit1, bit2 = BIT(m), BIT(m)
        arr1, arr2 = [nums[0]], [nums[1]]
        bit1.add(rank[nums[0]])
        bit2.add(rank[nums[1]])
        for x in nums[2:]:
            r = rank[x]
            g1, g2 = bit1.greater(r), bit2.greater(r)
            if g1 > g2 or (g1 == g2 and len(arr1) <= len(arr2)):
                arr1.append(x)
                bit1.add(r)
            else:
                arr2.append(x)
                bit2.add(r)
        return arr1 + arr2
# @lc code=end
