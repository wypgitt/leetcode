"""
Approach: Long division with a remainder-to-output-position map.
Data structure: the dictionary records where each remainder first appeared; a repeated remainder identifies the repeating decimal cycle.
Interview logic: integer division gives each decimal digit. If the remainder becomes zero, the decimal terminates. If a remainder repeats, the digits between the first occurrence and now repeat forever.
Complexity: O(k) time and space where k is the number of produced decimal digits before termination or repeat.
Tests and edge cases: negative signs; numerator zero; repeating fractions like 1/3; terminating fractions like 1/2.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def fractionToDecimal(self, numerator: int, denominator: int) -> str:
        if numerator == 0:
            return '0'
        sign = '-' if (numerator < 0) ^ (denominator < 0) else ''
        numerator, denominator = abs(numerator), abs(denominator)
        integer, rem = divmod(numerator, denominator)
        if rem == 0:
            return sign + str(integer)
        out = [sign + str(integer), '.']
        seen = {}
        while rem:
            if rem in seen:
                idx = seen[rem]
                out.insert(idx, '(')
                out.append(')')
                break
            seen[rem] = len(out)
            rem *= 10
            digit, rem = divmod(rem, denominator)
            out.append(str(digit))
        return ''.join(out)
# @lc code=end
