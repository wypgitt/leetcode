#
# @lc app=leetcode id=3348 lang=python3
#
# [3348] Smallest Divisible Digit Product II
#
# https://leetcode.com/problems/smallest-divisible-digit-product-ii/description/
#
# algorithms
# Hard (15.28%)
# Likes:    63
# Dislikes: 19
# Total Accepted:    5.3K
# Total Submissions: 34.4K
# Testcase Example:  "\"1234\"\n256"
#
#
# You are given a string num which represents a positive integer, and an
# integer t.
#
# A number is called zero-free if none of its digits are 0.
#
# Return a string representing the smallest zero-free number greater than
# or equal to num such that the product of its digits is divisible by t.
# If no such number exists, return "-1".
#
# Example 1:
#
# Input: num = "1234", t = 256
#
# Output: "1488"
#
# Explanation:
#
# The smallest zero-free number that is greater than 1234 and has the
# product of its digits divisible by 256 is 1488, with the product of its
# digits equal to 256.
#
# Example 2:
#
# Input: num = "12355", t = 50
#
# Output: "12355"
#
# Explanation:
#
# 12355 is already zero-free and has the product of its digits divisible
# by 50, with the product of its digits equal to 150.
#
# Example 3:
#
# Input: num = "11111", t = 26
#
# Output: "-1"
#
# Explanation:
#
# No number greater than 11111 has the product of its digits divisible by
# 26.
#
# Constraints:
#
# 2 <= num.length <= 2 * 10^5
#
# num consists only of digits in the range ['0', '9'].
#
# num does not contain leading zeros.
#
# 1 <= t <= 10^14
#

# @lc code=start

from collections import Counter


FACTOR_COUNTS = {
    0: Counter(),
    1: Counter(),
    2: Counter([2]),
    3: Counter([3]),
    4: Counter([2, 2]),
    5: Counter([5]),
    6: Counter([2, 3]),
    7: Counter([7]),
    8: Counter([2, 2, 2]),
    9: Counter([3, 3]),
}


class Solution:
    def smallestNumber(self, num: str, t: int) -> str:
        """
        Interview explanation:
        Smallest zero-free number ≥ num whose digit product is divisible by t.
        Digit products only involve primes 2,3,5,7 — if t has other primes → -1.
        Pack remaining prime powers into fewest digits (prefer 8,9,6,4,...).

        Algorithm:
        - Factor t into 2/3/5/7; greedily map exponents to digits 2..9.
        - If num already works (no zeros, primes covered), return it.
        - Else walk from the right: bump a digit, fill rest with 1s + needed digits.
        - If same length impossible, build shortest longer number.

        Complexity: O(len(num) + log t) time, O(len(num)) space.
        """
        prime_count, ok = self._get_prime_count(t)
        if not ok:
            return "-1"

        factor_count = self._get_factor_count(prime_count)
        if sum(factor_count.values()) > len(num):
            return "".join(d * factor_count[d] for d in "23456789")

        prefix = sum((FACTOR_COUNTS[int(c)] for c in num), start=Counter())
        first_zero = next((i for i, d in enumerate(num) if d == "0"), len(num))
        if first_zero == len(num) and prime_count <= prefix:
            return num

        for i in range(len(num) - 1, -1, -1):
            d = int(num[i])
            prefix -= FACTOR_COUNTS[d]
            space = len(num) - 1 - i
            if i > first_zero:
                continue
            for bigger in range(d + 1, 10):
                need = prime_count - prefix - FACTOR_COUNTS[bigger]
                factors = self._get_factor_count(need)
                if sum(factors.values()) <= space:
                    fill = space - sum(factors.values())
                    return (
                        num[:i]
                        + str(bigger)
                        + "1" * fill
                        + "".join(d * factors[d] for d in "23456789")
                    )

        factor_count = self._get_factor_count(prime_count)
        return (
            "1" * (len(num) + 1 - sum(factor_count.values()))
            + "".join(d * factor_count[d] for d in "23456789")
        )

    def _get_prime_count(self, t: int) -> tuple[Counter, bool]:
        count = Counter()
        for p in (2, 3, 5, 7):
            while t % p == 0:
                t //= p
                count[p] += 1
        return count, t == 1

    def _get_factor_count(self, count: Counter) -> dict[str, int]:
        count8, rem2 = divmod(count[2], 3)
        count9, count3 = divmod(count[3], 2)
        count4, count2 = divmod(rem2, 2)
        if count2 == 1 and count3 == 1:
            count2, count3, count6 = 0, 0, 1
        else:
            count6 = 0
        if count3 == 1 and count4 == 1:
            count2, count6, count3, count4 = 1, 1, 0, 0
        return {
            "2": count2,
            "3": count3,
            "4": count4,
            "5": count[5],
            "6": count6,
            "7": count[7],
            "8": count8,
            "9": count9,
        }
# @lc code=end
