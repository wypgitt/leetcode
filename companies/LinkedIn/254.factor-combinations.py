"""
Approach: Backtracking over nondecreasing factors.
Data structure: the path list stores factors chosen so far; recursion carries the minimum next factor to avoid duplicate permutations.
Interview logic: for each factor f from start to sqrt(target), if f divides target, then path + [f, target/f] is one valid combination, and recursion continues factoring target/f using factors >= f.
Complexity: output-sensitive; roughly O(number of factor combinations * combination length), O(log n) recursion depth in typical cases.
Tests and edge cases: primes return []; n=1 returns []; combinations are nondecreasing and therefore unique.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def getFactors(self, n: int) -> List[List[int]]:
        ans = []
        def dfs(start: int, target: int, path: List[int]) -> None:
            factor = start
            while factor * factor <= target:
                if target % factor == 0:
                    ans.append(path + [factor, target // factor])
                    dfs(factor, target // factor, path + [factor])
                factor += 1
        dfs(2, n, [])
        return ans
# @lc code=end
