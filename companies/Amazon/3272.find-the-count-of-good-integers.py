#
# @lc app=leetcode id=3272 lang=python3
#
# [3272] Find the Count of Good Integers
#
# https://leetcode.com/problems/find-the-count-of-good-integers/description/
#
# algorithms
# Hard (69.25%)
# Likes:    473
# Dislikes: 112
# Total Accepted:    73.4K
# Total Submissions: 105.9K
# Testcase Example:  "3\n5"
#
#
# You are given two positive integers n and k.
#
# An integer x is called k-palindromic if:
#
# x is a palindrome.
#
# x is divisible by k.
#
# An integer is called good if its digits can be rearranged to form a
# k-palindromic integer. For example, for k = 2, 2020 can be rearranged to
# form the k-palindromic integer 2002, whereas 1010 cannot be rearranged
# to form a k-palindromic integer.
#
# Return the count of good integers containing n digits.
#
# Note that any integer must not have leading zeros, neither before nor
# after rearrangement. For example, 1010 cannot be rearranged to form 101.
#
# Example 1:
#
# Input: n = 3, k = 5
#
# Output: 27
#
# Explanation:
#
# Some of the good integers are:
#
# 551 because it can be rearranged to form 515.
#
# 525 because it is already k-palindromic.
#
# Example 2:
#
# Input: n = 1, k = 4
#
# Output: 2
#
# Explanation:
#
# The two good integers are 4 and 8.
#
# Example 3:
#
# Input: n = 5, k = 6
#
# Output: 2468
#
# Constraints:
#
# 1 <= n <= 10
#
# 1 <= k <= 9
#

# @lc code=start

from math import factorial


class Solution:
    def countGoodIntegers(self, n: int, k: int) -> int:
        """
        Interview explanation:
        A good n-digit number rearranges (no leading zero) into a palindrome
        divisible by k. Enumerate half-palindromes, keep distinct digit multisets
        of valid k-palindromes, sum rearrangement counts.

        Algorithm:
        - Generate all n-digit palindromes via the first ceil(n/2) digits.
        - If pal % k == 0, record sorted digit signature in a set.
        - For each signature, count permutations of digits with nonzero first digit.

        Complexity: O(10^{ceil(n/2)} * n) time, O(10^{ceil(n/2)}) space.
        """
        half = (n + 1) // 2
        start = 10 ** (half - 1) if n > 1 else 0
        end = 10 ** half
        seen: set[str] = set()
        for pref in range(start, end):
            left = str(pref)
            if n % 2 == 0:
                pal = left + left[::-1]
            else:
                pal = left + left[:-1][::-1]
            if int(pal) % k == 0:
                seen.add(''.join(sorted(pal)))

        ans = 0
        for sig in seen:
            cnt = [0] * 10
            for ch in sig:
                cnt[int(ch)] += 1
            # total permutations with no leading zero
            total = 0
            for first in range(1, 10):
                if cnt[first] == 0:
                    continue
                cnt[first] -= 1
                ways = factorial(n - 1)
                for c in cnt:
                    ways //= factorial(c)
                total += ways
                cnt[first] += 1
            ans += total
        return ans
# @lc code=end
