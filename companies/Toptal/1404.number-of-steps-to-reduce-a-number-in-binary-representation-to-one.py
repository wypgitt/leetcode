#
# @lc app=leetcode id=1404 lang=python3
#
# [1404] Number of Steps to Reduce a Number in Binary Representation to One
#
# https://leetcode.com/problems/number-of-steps-to-reduce-a-number-in-binary-representation-to-one/description/
#
# algorithms
# Medium (63.75%)
# Likes:    1752
# Dislikes: 101
# Total Accepted:    272K
# Total Submissions: 427K
# Testcase Example:  "\"1101\""
#
# Given the binary representation of an integer as a string s, return the
# number of steps to reduce it to 1 under the following rules:
#
# If the current number is even, you have to divide it by 2.
#
# If the current number is odd, you have to add 1 to it.
#
# It is guaranteed that you can always reach one for all test cases.
#
# Example 1:
#
# Input: s = "1101"
# Output: 6
# Explanation: "1101" corressponds to number 13 in their decimal
# representation.
# Step 1) 13 is odd, add 1 and obtain 14.
# Step 2) 14 is even, divide by 2 and obtain 7.
# Step 3) 7 is odd, add 1 and obtain 8.
# Step 4) 8 is even, divide by 2 and obtain 4.
# Step 5) 4 is even, divide by 2 and obtain 2.
# Step 6) 2 is even, divide by 2 and obtain 1.
#
# Example 2:
#
# Input: s = "10"
# Output: 1
# Explanation: "10" corresponds to number 2 in their decimal representation.
# Step 1) 2 is even, divide by 2 and obtain 1.
#
# Example 3:
#
# Input: s = "1"
# Output: 0
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of characters '0' or '1'
#
# s[0] == '1'
#

# @lc code=start
class Solution:
    def numSteps(self, s: str) -> int:
        """
        Interview explanation:
        Simulate divide-by-2 (right shift when even) and add-1 (when odd) on a
        binary string without converting to int. Track carry for +1 from the right.

        Algorithm:
        (simulate string / carry)
        - Walk from rightmost bit (except leading 1): if bit^carry==0 → even step (+1);
          else odd → +1 then will become even (+2 total) and set carry.
        - Classic: count ops while processing bits with carry.

        Complexity: O(n) time, O(1) space.
        """
        steps = 0
        carry = 0
        # Process from LSB to just before MSB
        for i in range(len(s) - 1, 0, -1):
            bit = int(s[i]) + carry
            if bit % 2 == 0:
                # even: divide by 2
                steps += 1
            else:
                # odd: add 1 (makes even) then divide — carry continues
                steps += 2
                carry = 1
        return steps + carry

    def numSteps_int(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: convert to int and simulate Collatz-like ops (Python bigints OK).

        Algorithm:
        - n=int(s,2); while n>1: n = n+1 if n odd else n//2; count++

        Complexity: O(n) steps worst-case for value ~2^n, O(n) space for bigint.
        """
        n = int(s, 2)
        steps = 0
        while n > 1:
            if n & 1:
                n += 1
            else:
                n >>= 1
            steps += 1
        return steps
# @lc code=end
