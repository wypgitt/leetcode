#
# @lc app=leetcode id=1342 lang=python3
#
# [1342] Number of Steps to Reduce a Number to Zero
#
# https://leetcode.com/problems/number-of-steps-to-reduce-a-number-to-zero/description/
#
# algorithms
# Easy (85.87%)
# Likes:    4312
# Dislikes: 182
# Total Accepted:    955K
# Total Submissions: 1.1M
# Testcase Example:  "14"
#
# Given an integer num, return the number of steps to reduce it to zero.
#
# In one step, if the current number is even, you have to divide it by 2,
# otherwise, you have to subtract 1 from it.
#
# Example 1:
#
# Input: num = 14
# Output: 6
# Explanation:
# Step 1) 14 is even; divide by 2 and obtain 7.
# Step 2) 7 is odd; subtract 1 and obtain 6.
# Step 3) 6 is even; divide by 2 and obtain 3.
# Step 4) 3 is odd; subtract 1 and obtain 2.
# Step 5) 2 is even; divide by 2 and obtain 1.
# Step 6) 1 is odd; subtract 1 and obtain 0.
#
# Example 2:
#
# Input: num = 8
# Output: 4
# Explanation:
# Step 1) 8 is even; divide by 2 and obtain 4.
# Step 2) 4 is even; divide by 2 and obtain 2.
# Step 3) 2 is even; divide by 2 and obtain 1.
# Step 4) 1 is odd; subtract 1 and obtain 0.
#
# Example 3:
#
# Input: num = 123
# Output: 12
#
# Constraints:
#
# 0 <= num <= 10^6
#

# @lc code=start
class Solution:
    def numberOfSteps(self, num: int) -> int:
        """
        Interview explanation:
        If even divide by 2 else subtract 1; count steps to 0. Simulate or use
        bit facts: steps = bits + (#1 bits - 1) for num>0.

        Algorithm (simulation):
        - While num: if even >>=1 else -=1; steps++.

        Complexity: O(log num) time, O(1) space.
        """
        steps = 0
        while num:
            if num & 1:
                num -= 1
            else:
                num >>= 1
            steps += 1
        return steps

    def numberOfSteps_bits(self, num: int) -> int:
        """
        Interview explanation:
        Alternate bit formula: each 1 (except leading) needs a subtract; each
        bit position needs a shift. steps = floor(log2)+popcount for num>0.

        Algorithm:
        - If 0 return 0; return num.bit_length()-1 + bin(num).count('1').

        Complexity: O(log num) time, O(1) space.
        """
        if num == 0:
            return 0
        return num.bit_length() - 1 + bin(num).count("1")
# @lc code=end

