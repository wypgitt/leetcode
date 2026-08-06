#
# @lc app=leetcode id=2354 lang=python3
#
# [2354] Number of Excellent Pairs
#
# https://leetcode.com/problems/number-of-excellent-pairs/description/
#
# algorithms
# Hard (49.40%)
# Likes:    624
# Dislikes: 25
# Total Accepted:    19.3K
# Total Submissions: 39.1K
# Testcase Example:  "[1,2,3,1]\n3"
#
# You are given a 0-indexed positive integer array nums and a positive integer
# k.
#
# A pair of numbers (num1, num2) is called excellent if the following conditions
# are satisfied:
#
#
# Both the numbers num1 and num2 exist in the array nums.
#
#
# The sum of the number of set bits in num1 OR num2 and num1 AND num2 is greater
# than or equal to k, where OR is the bitwise OR operation and AND is the
# bitwise AND operation.
#
# Return the number of distinct excellent pairs.
#
# Two pairs (a, b) and (c, d) are considered distinct if either a != c or b !=
# d. For example, (1, 2) and (2, 1) are distinct.
#
# Note that a pair (num1, num2) such that num1 == num2 can also be excellent if
# you have at least one occurrence of num1 in the array.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3,1], k = 3
# Output: 5
# Explanation: The excellent pairs are the following:
# - (3, 3). (3 AND 3) and (3 OR 3) are both equal to (11) in binary. The total
# number of set bits is 2 + 2 = 4, which is greater than or equal to k = 3.
# - (2, 3) and (3, 2). (2 AND 3) is equal to (10) in binary, and (2 OR 3) is
# equal to (11) in binary. The total number of set bits is 1 + 2 = 3.
# - (1, 3) and (3, 1). (1 AND 3) is equal to (01) in binary, and (1 OR 3) is
# equal to (11) in binary. The total number of set bits is 1 + 2 = 3.
# So the number of excellent pairs is 5.
#
# Example 2:
#
# Input: nums = [5,1,1], k = 10
# Output: 0
# Explanation: There are no excellent pairs for this array.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#
#
# 1 <= k <= 60
#

# @lc code=start

from typing import List


class Solution:
    def countExcellentPairs(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Excellent pair (a,b): a|b and a&b both defined from distinct nums set,
        and bitcount(a|b)+bitcount(a&b) >= k. Note bitcount(a|b)+bitcount(a&b)
        = bitcount(a)+bitcount(b). Count ordered pairs (incl. a==b).

        Algorithm:
        - Unique nums; count by popcount; two pointers / suffix on sorted counts.

        Complexity: O(n log A + B^2) or O(n + B) with B<=32.
        """
        uniq = set(nums)
        cnt = [0] * 33
        for x in uniq:
            cnt[x.bit_count()] += 1
        ans = 0
        for i in range(33):
            for j in range(33):
                if i + j >= k:
                    ans += cnt[i] * cnt[j]
        return ans

    def countExcellentPairs_two_pointers(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: sort popcounts; two pointers count pairs with sum >= k.

        Algorithm:
        - bits sorted; for each i, advance j while bits[i]+bits[j] < k.

        Complexity: O(n log n) time, O(n) space.
        """
        bits = sorted(x.bit_count() for x in set(nums))
        n = len(bits)
        ans = 0
        j = n
        for i in range(n):
            while j > 0 and bits[i] + bits[j - 1] >= k:
                j -= 1
            ans += n - j
        return ans
# @lc code=end
