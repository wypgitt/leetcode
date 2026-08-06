#
# @lc app=leetcode id=412 lang=python3
#
# [412] Fizz Buzz
#
# https://leetcode.com/problems/fizz-buzz/description/
#
# algorithms
# Easy (75.77%)
# Likes:    3442
# Dislikes: 472
# Total Accepted:    1.9M
# Total Submissions: 2.5M
# Testcase Example:  "3"
#
# Given an integer n, return a string array answer (1-indexed) where:
#
# answer[i] == "FizzBuzz" if i is divisible by 3 and 5.
#
# answer[i] == "Fizz" if i is divisible by 3.
#
# answer[i] == "Buzz" if i is divisible by 5.
#
# answer[i] == i (as a string) if none of the above conditions are true.
#
# Example 1:
#
# Input: n = 3
# Output: ["1","2","Fizz"]
#
# Example 2:
#
# Input: n = 5
# Output: ["1","2","Fizz","4","Buzz"]
#
# Example 3:
#
# Input: n = 15
# Output:
# ["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]
#
# Constraints:
#
# 1 <= n <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        """
        Interview explanation:
        Classic FizzBuzz: for each i in 1..n map multiples of 3/5/15 to the
        corresponding strings, else the number itself.

        Algorithm:
        - For i=1..n: if %15 FizzBuzz; elif %3 Fizz; elif %5 Buzz; else str(i).

        Complexity: O(n) time, O(n) space for output.
        """
        ans = []
        for i in range(1, n + 1):
            if i % 15 == 0:
                ans.append("FizzBuzz")
            elif i % 3 == 0:
                ans.append("Fizz")
            elif i % 5 == 0:
                ans.append("Buzz")
            else:
                ans.append(str(i))
        return ans
# @lc code=end
