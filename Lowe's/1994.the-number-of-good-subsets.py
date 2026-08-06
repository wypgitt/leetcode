#
# @lc app=leetcode id=1994 lang=python3
#
# [1994] The Number of Good Subsets
#
# https://leetcode.com/problems/the-number-of-good-subsets/description/
#
# algorithms
# Hard (37.67%)
# Likes:    515
# Dislikes: 17
# Total Accepted:    12.0K
# Total Submissions: 31.9K
# Testcase Example:  "[1,2,3,4]"
#
# You are given an integer array nums. We call a subset of nums good if its
# product can be represented as a product of one or more distinct prime
# numbers.
#
# For example, if nums = [1, 2, 3, 4]:
#
# [2, 3], [1, 2, 3], and [1, 3] are good subsets with products 6 = 2*3, 6 =
# 2*3, and 3 = 3 respectively.
#
# [1, 4] and [4] are not good subsets with products 4 = 2*2 and 4 = 2*2
# respectively.
#
# Return the number of different good subsets in nums modulo 10^9 + 7.
#
# A subset of nums is any array that can be obtained by deleting some (possibly
# none or all) elements from nums. Two subsets are different if and only if the
# chosen indices to delete are different.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: 6
# Explanation: The good subsets are:
# - [1,2]: product is 2, which is the product of distinct prime 2.
# - [1,2,3]: product is 6, which is the product of distinct primes 2 and 3.
# - [1,3]: product is 3, which is the product of distinct prime 3.
# - [2]: product is 2, which is the product of distinct prime 2.
# - [2,3]: product is 6, which is the product of distinct primes 2 and 3.
# - [3]: product is 3, which is the product of distinct prime 3.
#
# Example 2:
#
# Input: nums = [4,2,3,15]
# Output: 5
# Explanation: The good subsets are:
# - [2]: product is 2, which is the product of distinct prime 2.
# - [2,3]: product is 6, which is the product of distinct primes 2 and 3.
# - [2,15]: product is 30, which is the product of distinct primes 2, 3, and 5.
# - [3]: product is 3, which is the product of distinct prime 3.
# - [15]: product is 15, which is the product of distinct primes 3 and 5.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 30
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def numberOfGoodSubsets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count nonempty subsets whose product is square-free (no squared prime
        factor), times ways to include optional 1s. Bit DP over 10 primes.

        Algorithm:
        - Primes = [2,3,5,7,11,13,17,19,23,29]; mask for square-free 2..30.
        - Skip numbers with square factors; freq count; DP masks; multiply 2^freq[1].

        Complexity: O(30 * 2^P + n) time, O(2^P) space.
        """
        MOD = 10**9 + 7
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        freq = Counter(nums)

        def mask_of(x: int):
            m = 0
            for i, p in enumerate(primes):
                cnt = 0
                while x % p == 0:
                    x //= p
                    cnt += 1
                    if cnt > 1:
                        return -1
                if cnt:
                    m |= 1 << i
            return m if x == 1 else -1

        dp = [0] * (1 << len(primes))
        dp[0] = 1
        for x in range(2, 31):
            if freq[x] == 0:
                continue
            m = mask_of(x)
            if m < 0:
                continue
            for state in range((1 << len(primes)) - 1, -1, -1):
                if state & m:
                    continue
                dp[state | m] = (dp[state | m] + dp[state] * freq[x]) % MOD

        ans = sum(dp[1:]) % MOD
        # multiply by 2^{freq[1]} ways to include ones
        ans = ans * pow(2, freq[1], MOD) % MOD
        return ans

    def numberOfGoodSubsets_clarity(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate same prime-mask DP with an explicit square-free filter list.

        Algorithm:
        - Precompute masks for 1..30; iterate freq; update knapsack-style masks.

        Complexity: O(2^10 * 30 + n) time, O(2^10) space.
        """
        MOD = 10**9 + 7
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        masks = [-1] * 31
        for x in range(1, 31):
            y, m = x, 0
            ok = True
            for i, p in enumerate(primes):
                c = 0
                while y % p == 0:
                    y //= p
                    c += 1
                if c > 1:
                    ok = False
                    break
                if c:
                    m |= 1 << i
            masks[x] = m if ok and y == 1 else -1

        freq = Counter(nums)
        dp = [0] * (1 << 10)
        dp[0] = 1
        for x in range(2, 31):
            if freq[x] == 0 or masks[x] < 0:
                continue
            m = masks[x]
            for s in range((1 << 10) - 1, -1, -1):
                if s & m == 0:
                    dp[s | m] = (dp[s | m] + dp[s] * freq[x]) % MOD
        total = sum(dp[1:]) % MOD
        return total * pow(2, freq[1], MOD) % MOD
# @lc code=end

