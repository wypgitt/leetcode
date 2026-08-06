"""
Approach: Count factors of 5 in n!.
Data structure: a running integer count is sufficient.
Interview logic: each trailing zero comes from a factor pair 2*5, and factorials contain more factors of 2 than 5. Numbers like 25 contribute multiple factors of 5, handled by repeatedly dividing n by 5.
Complexity: O(log_5 n) time, O(1) space.
Tests and edge cases: n < 5 returns 0; powers of 5 add extra counts; large n remains fast.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def trailingZeroes(self, n: int) -> int:
        count = 0
        while n:
            n //= 5
            count += n
        return count
# @lc code=end
