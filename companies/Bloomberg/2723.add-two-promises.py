#
# @lc app=leetcode id=2723 lang=python3
#
# [2723] Add Two Promises
#
# https://leetcode.com/problems/add-two-promises/description/
#
# algorithms
# Easy (91.69%)
# Likes:    373
# Dislikes: 33
# Total Accepted:    195.8K
# Total Submissions: 213.5K
# Testcase Example:  "new Promise(resolve => setTimeout(() => resolve(2), 20))\nnew Promise(resolve => setTimeout(() => resolve(5), 60))"
#
# Given two promises promise1 and promise2, return a new promise. promise1 and
# promise2 will both resolve with a number. The returned promise should resolve
# with the sum of the two numbers.
#
#
#
# Example 1:
#
# Input:
# promise1 = new Promise(resolve => setTimeout(() => resolve(2), 20)),
# promise2 = new Promise(resolve => setTimeout(() => resolve(5), 60))
# Output: 7
# Explanation: The two input promises resolve with the values of 2 and 5
# respectively. The returned promise should resolve with a value of 2 + 5 = 7.
# The time the returned promise resolves is not judged for this problem.
#
# Example 2:
#
# Input:
# promise1 = new Promise(resolve => setTimeout(() => resolve(10), 50)),
# promise2 = new Promise(resolve => setTimeout(() => resolve(-12), 30))
# Output: -2
# Explanation: The two input promises resolve with the values of 10 and -12
# respectively. The returned promise should resolve with a value of 10 + -12 =
# -2.
#
#
#
# Constraints:
#
#
# promise1 and promise2 are promises that resolve with a number
#

# @lc code=start
import asyncio
from typing import Awaitable


class Solution:
    async def addTwoPromises(self, promise1: Awaitable[int], promise2: Awaitable[int]) -> int:
        """
        Interview explanation:
        JavaScript problem (Python analog): await two numeric awaitables and return sum.

        Algorithm:
        - a,b = await gather; return a+b.

        Complexity: O(1) plus await time of both.
        """
        a, b = await asyncio.gather(promise1, promise2)
        return a + b
# @lc code=end
