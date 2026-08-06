#
# @lc app=leetcode id=2708 lang=python3
#
# [2708] Maximum Strength of a Group
#
# https://leetcode.com/problems/maximum-strength-of-a-group/description/
#
# algorithms
# Medium (25.87%)
# Likes:    388
# Dislikes: 68
# Total Accepted:    39.7K
# Total Submissions: 153.3K
# Testcase Example:  "[3,-1,-5,2,5,-9]"
#
# You are given a 0-indexed integer array nums representing the score of
# students in an exam. The teacher would like to form one non-empty group of
# students with maximal strength, where the strength of a group of students of
# indices i_0, i_1, i_2, ... , i_k is defined as nums[i_0] * nums[i_1] *
# nums[i_2] * ... * nums[i_k​].
#
# Return the maximum strength of a group the teacher can create.
#
#
#
# Example 1:
#
# Input: nums = [3,-1,-5,2,5,-9]
# Output: 1350
# Explanation: One way to form a group of maximal strength is to group the
# students at indices [0,2,3,4,5]. Their strength is 3 * (-5) * 2 * 5 * (-9) =
# 1350, which we can show is optimal.
#
# Example 2:
#
# Input: nums = [-4,-5,-4]
# Output: 20
# Explanation: Group the students at indices [0, 1] . Then, we’ll have a
# resulting strength of 20. We cannot achieve greater strength.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 13
#
#
# -9 <= nums[i] <= 9
#

# @lc code=start
from typing import List


class Solution:
    def maxStrength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Nonempty subset product ("strength") maximized.

        Algorithm:
        - Multiply all non-zero; if odd count of negatives, divide out the negative
          closest to zero. Handle all-nonpositive edge cases carefully.

        Complexity: O(n) time, O(1) space.
        """
        if len(nums) == 1:
            return nums[0]
        prod = 1
        neg = []
        has_pos = False
        zeros = 0
        for x in nums:
            if x > 0:
                prod *= x
                has_pos = True
            elif x < 0:
                prod *= x
                neg.append(x)
            else:
                zeros += 1
        if not neg and not has_pos:
            return 0
        if len(neg) % 2 == 1:
            # remove weakest negative (largest algebraically)
            weak = max(neg)
            prod //= weak
            if prod == 1 and not has_pos:
                # only negatives; after remove one maybe empty product
                if len(neg) == 1:
                    return 0 if zeros else neg[0]
        return prod
# @lc code=end
