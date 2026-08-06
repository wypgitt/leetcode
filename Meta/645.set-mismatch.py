#
# @lc app=leetcode id=645 lang=python3
#
# [645] Set Mismatch
#
# https://leetcode.com/problems/set-mismatch/description/
#
# algorithms
# Easy (43.39%)
# Likes:    5572
# Dislikes: 1436
# Total Accepted:    806K
# Total Submissions: 1.9M
# Testcase Example:  "[1,2,2,4]"
#
# You have a set of integers s, which originally contains all the numbers from
# 1 to n. Unfortunately, due to some error, one of the numbers in s got
# duplicated to another number in the set, which results in repetition of one
# number and loss of another number.
#
# You are given an integer array nums representing the data status of this set
# after the error.
#
# Find the number that occurs twice and the number that is missing and return
# them in the form of an array.
#
# Example 1:
#
# Input: nums = [1,2,2,4]
# Output: [2,3]
#
# Example 2:
#
# Input: nums = [1,1]
# Output: [1,2]
#
# Constraints:
#
# 2 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def findErrorNums(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Numbers 1..n with one duplicate and one missing. Use XOR or marking /
        math: duplicate = sum - sum(set); missing from expected.

        Algorithm:
        - dup from seen set (or index marking).
        - missing = expected_sum - (total - dup).

        Complexity: O(N) time, O(N) set (or O(1) with marking/XOR).
        """
        seen = set()
        dup = -1
        total = 0
        for x in nums:
            if x in seen:
                dup = x
            seen.add(x)
            total += x
        n = len(nums)
        missing = n * (n + 1) // 2 - (total - dup)
        return [dup, missing]
# @lc code=end
