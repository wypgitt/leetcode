#
# @lc app=leetcode id=2621 lang=python3
#
# [2621] Sleep
#
# https://leetcode.com/problems/sleep/description/
#
# algorithms
# Easy (87.33%)
# Likes:    723
# Dislikes: 61
# Total Accepted:    263.6K
# Total Submissions: 301.8K
# Testcase Example:  "100"
#
# Given a positive integer millis, write an asynchronous function that sleeps
# for millis milliseconds. It can resolve any value.
#
# Note that minor deviation from millis in the actual sleep duration is
# acceptable.
#
#
#
# Example 1:
#
# Input: millis = 100
# Output: 100
# Explanation: It should return a promise that resolves after 100ms.
# let t = Date.now();
# sleep(100).then(() => {
#   console.log(Date.now() - t); // 100
# });
#
# Example 2:
#
# Input: millis = 200
# Output: 200
# Explanation: It should return a promise that resolves after 200ms.
#
#
#
# Constraints:
#
#
# 1 <= millis <= 1000
#

# @lc code=start
import asyncio


async def sleep(millis: int) -> None:
    """
    Interview explanation:
    Async sleep for millis milliseconds (JS Promise-based sleep port).

    Algorithm:
    - await asyncio.sleep converting milliseconds to seconds.

    Complexity: O(1) work besides waiting millis ms.
    """
    await asyncio.sleep(millis / 1000.0)


class Solution:
    async def sleep(self, millis: int) -> None:
        """
        Interview explanation:
        Thin Solution wrapper for async sleep.

        Algorithm:
        - Delegate to sleep(millis).

        Complexity: O(1) besides waiting.
        """
        await sleep(millis)
# @lc code=end
