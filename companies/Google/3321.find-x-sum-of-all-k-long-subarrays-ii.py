#
# @lc app=leetcode id=3321 lang=python3
#
# [3321] Find X-Sum of All K-Long Subarrays II
#
# https://leetcode.com/problems/find-x-sum-of-all-k-long-subarrays-ii/description/
#
# algorithms
# Hard (41.22%)
# Likes:    453
# Dislikes: 51
# Total Accepted:    66.1K
# Total Submissions: 160.4K
# Testcase Example:  "[1,1,2,2,3,4,2,3]\n6\n2"
#
#
# You are given an array nums of n integers and two integers k and x.
#
# The x-sum of an array is calculated by the following procedure:
#
# Count the occurrences of all elements in the array.
#
# Keep only the occurrences of the top x most frequent elements. If two
# elements have the same number of occurrences, the element with the
# bigger value is considered more frequent.
#
# Calculate the sum of the resulting array.
#
# Note that if an array has less than x distinct elements, its x-sum is
# the sum of the array.
#
# Return an integer array answer of length n - k + 1 where answer[i] is
# the x-sum of the subarray nums[i..i + k - 1].
#
# Example 1:
#
# Input: nums = [1,1,2,2,3,4,2,3], k = 6, x = 2
#
# Output: [6,10,12]
#
# Explanation:
#
# For subarray [1, 1, 2, 2, 3, 4], only elements 1 and 2 will be kept in
# the resulting array. Hence, answer[0] = 1 + 1 + 2 + 2.
#
# For subarray [1, 2, 2, 3, 4, 2], only elements 2 and 4 will be kept in
# the resulting array. Hence, answer[1] = 2 + 2 + 2 + 4. Note that 4 is
# kept in the array since it is bigger than 3 and 1 which occur the same
# number of times.
#
# For subarray [2, 2, 3, 4, 2, 3], only elements 2 and 3 are kept in the
# resulting array. Hence, answer[2] = 2 + 2 + 2 + 3 + 3.
#
# Example 2:
#
# Input: nums = [3,8,7,8,7,5], k = 2, x = 2
#
# Output: [11,15,15,15,12]
#
# Explanation:
#
# Since k == x, answer[i] is equal to the sum of the subarray nums[i..i +
# k - 1].
#
# Constraints:
#
# nums.length == n
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= x <= k <= nums.length
#

# @lc code=start

from collections import Counter
from typing import List

try:
    from sortedcontainers import SortedList
except ImportError:  # pragma: no cover
    SortedList = None  # type: ignore


class Solution:
    def findXSum(self, nums: List[int], k: int, x: int) -> List[int]:
        """
        Interview explanation:
        Sliding-window x-sum: keep the top-x (freq, value) pairs; sum freq*value
        over that set. Ties break toward larger values.

        Algorithm:
        - Maintain Counter + two SortedLists: top (size <= x) and bot (rest).
        - On freq change, remove old (freq, val), insert new into bot, then rebalance
          by promoting/demoting so top holds the x largest pairs.
        - Record top-sum for each window of length k.

        Complexity: O(n log n) time, O(n) space.
        """
        if SortedList is None:
            raise ImportError("sortedcontainers is required for findXSum")

        count: Counter = Counter()
        top: SortedList = SortedList()
        bot: SortedList = SortedList()
        window_sum = 0
        ans: List[int] = []

        def update(num: int, delta: int) -> None:
            nonlocal window_sum
            if count[num] > 0:
                pair = (count[num], num)
                if pair in bot:
                    bot.remove(pair)
                else:
                    top.remove(pair)
                    window_sum -= num * count[num]
            count[num] += delta
            if count[num] > 0:
                bot.add((count[num], num))

        def rebalance() -> None:
            nonlocal window_sum
            while bot and len(top) < x:
                freq, val = bot.pop()
                top.add((freq, val))
                window_sum += freq * val
            while len(top) > x:
                freq, val = top.pop(0)
                window_sum -= freq * val
                bot.add((freq, val))
            while bot and top and bot[-1] > top[0]:
                bf, bv = bot.pop()
                tf, tv = top.pop(0)
                bot.add((tf, tv))
                top.add((bf, bv))
                window_sum += bf * bv - tf * tv

        for i, num in enumerate(nums):
            update(num, 1)
            if i >= k:
                update(nums[i - k], -1)
            rebalance()
            if i >= k - 1:
                ans.append(window_sum)
        return ans
# @lc code=end

