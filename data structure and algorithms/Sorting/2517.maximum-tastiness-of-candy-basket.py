#
# @lc app=leetcode id=2517 lang=python3
#
# [2517] Maximum Tastiness of Candy Basket
#
# https://leetcode.com/problems/maximum-tastiness-of-candy-basket/description/
#
# algorithms
# Medium (68.61%)
# Likes:    1093
# Dislikes: 185
# Total Accepted:    43.4K
# Total Submissions: 63.2K
# Testcase Example:  "[13,5,1,8,21,2]\n3"
#
# You are given an array of positive integers price where price[i] denotes the
# price of the i^th candy and a positive integer k.
#
# The store sells baskets of k distinct candies. The tastiness of a candy basket
# is the smallest absolute difference of the prices of any two candies in the
# basket.
#
# Return the maximum tastiness of a candy basket.
#
#
#
# Example 1:
#
# Input: price = [13,5,1,8,21,2], k = 3
# Output: 8
# Explanation: Choose the candies with the prices [13,5,21].
# The tastiness of the candy basket is: min(|13 - 5|, |13 - 21|, |5 - 21|) =
# min(8, 8, 16) = 8.
# It can be proven that 8 is the maximum tastiness that can be achieved.
#
# Example 2:
#
# Input: price = [1,3,1], k = 2
# Output: 2
# Explanation: Choose the candies with the prices [1,3].
# The tastiness of the candy basket is: min(|1 - 3|) = min(2) = 2.
# It can be proven that 2 is the maximum tastiness that can be achieved.
#
# Example 3:
#
# Input: price = [7,7,7,7], k = 2
# Output: 0
# Explanation: Choosing any two distinct candies from the candies we have will
# result in a tastiness of 0.
#
#
#
# Constraints:
#
#
# 2 <= k <= price.length <= 10^5
#
#
# 1 <= price[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumTastiness(self, price: List[int], k: int) -> int:
        """
        Interview explanation:
        Choose k distinct candies maximizing the minimum pairwise price gap
        (tastiness).

        Algorithm:
        (binary search on answer)
        - Sort prices; greedily pick next candy if price - last >= mid; check >= k.

        Complexity: O(n log n + n log(max-min)) time, O(n) space for sort.
        """
        price.sort()
        lo, hi = 0, price[-1] - price[0]
        ans = 0

        def can(t: int) -> bool:
            cnt = 1
            last = price[0]
            for p in price[1:]:
                if p - last >= t:
                    cnt += 1
                    last = p
                    if cnt >= k:
                        return True
            return False

        while lo <= hi:
            mid = (lo + hi) // 2
            if can(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
# @lc code=end
