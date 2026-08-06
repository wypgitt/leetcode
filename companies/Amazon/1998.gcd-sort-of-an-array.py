#
# @lc app=leetcode id=1998 lang=python3
#
# [1998] GCD Sort of an Array
#
# https://leetcode.com/problems/gcd-sort-of-an-array/description/
#
# algorithms
# Hard (50.6%)
# Likes:    547
# Dislikes: 15
# Total Accepted:    16.3K
# Total Submissions: 32.3K
# Testcase Example:  "[7,21,3]"
#
# You are given an integer array nums, and you can perform the following
# operation any number of times on nums:
#
# Swap the positions of two elements nums[i] and nums[j] if gcd(nums[i],
# nums[j]) > 1 where gcd(nums[i], nums[j]) is the greatest common divisor of
# nums[i] and nums[j].
#
# Return true if it is possible to sort nums in non-decreasing order using the
# above swap method, or false otherwise.
#
# Example 1:
#
# Input: nums = [7,21,3]
# Output: true
# Explanation: We can sort [7,21,3] by performing the following operations:
# - Swap 7 and 21 because gcd(7,21) = 7. nums = [21,7,3]
# - Swap 21 and 3 because gcd(21,3) = 3. nums = [3,7,21]
#
# Example 2:
#
# Input: nums = [5,2,6,2]
# Output: false
# Explanation: It is impossible to sort the array because 5 cannot be swapped
# with any other element.
#
# Example 3:
#
# Input: nums = [10,5,9,3,15]
# Output: true
# We can sort [10,5,9,3,15] by performing the following operations:
# - Swap 10 and 15 because gcd(10,15) = 5. nums = [15,5,9,3,10]
# - Swap 15 and 3 because gcd(15,3) = 3. nums = [3,5,9,15,10]
# - Swap 10 and 15 because gcd(10,15) = 5. nums = [3,5,9,10,15]
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# 2 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def gcdSort(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Can swap nums[i], nums[j] if gcd>1. Equivalent: numbers sharing a prime
        factor are in the same Union-Find component; check nums can become
        sorted within components (each value can move to any index in its component).

        Algorithm:
        - For each x, union x with its prime factors (or smallest prime factor sieve).
        - Compare sorted(nums) position-wise: nums[i] and sorted[i] same find().

        Complexity: O(A log log A + n α(A)) with sieve up to max(nums).
        """
        M = max(nums)
        spf = list(range(M + 1))
        for i in range(2, int(M**0.5) + 1):
            if spf[i] == i:
                for j in range(i * i, M + 1, i):
                    if spf[j] == j:
                        spf[j] = i

        parent = list(range(M + 1))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for x in nums:
            y = x
            while y > 1:
                p = spf[y]
                union(x, p)
                while y % p == 0:
                    y //= p

        for a, b in zip(nums, sorted(nums)):
            if find(a) != find(b):
                return False
        return True

    def gcdSort_factors(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: factor each number by trial division and union with factors
        (no full sieve; fine when n small / max large carefully).

        Algorithm:
        - Trial factor; UF on values+factors; compare to sorted.

        Complexity: O(n sqrt A α) time, O(A) space.
        """
        parent = {}

        def find(x: int) -> int:
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            parent.setdefault(a, a)
            parent.setdefault(b, b)
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        def factor(x: int):
            y = x
            d = 2
            while d * d <= y:
                if y % d == 0:
                    union(x, d)
                    while y % d == 0:
                        y //= d
                d += 1
            if y > 1:
                union(x, y)

        for x in nums:
            factor(x)
        return all(find(a) == find(b) for a, b in zip(nums, sorted(nums)))
# @lc code=end

