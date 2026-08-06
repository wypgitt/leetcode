#
# @lc app=leetcode id=3858 lang=python3
#
# [3858] Minimum Bitwise OR From Grid
#
# https://leetcode.com/problems/minimum-bitwise-or-from-grid/description/
#
# algorithms
# Medium (26.79%)
# Likes:    133
# Dislikes: 3
# Total Accepted:    14K
# Total Submissions: 52.2K
# Testcase Example:  '[[1,5],[2,4]]'
#
# You are given a 2D integer array grid of size m x n.
# 
# You must select exactly one integer from each row of the grid.
# 
# Return an integer denoting the minimum possible bitwise OR of the selected
# integers from each row.
# 
# 
# Example 1:
# 
# 
# Input: grid = [[1,5],[2,4]]
# 
# Output: 3
# 
# Explanation:
# 
# 
# Choose 1 from the first row and 2 from the second row.
# The bitwise OR of 1 | 2 = 3​​​​​​​, which is the minimum possible.
# 
# 
# 
# Example 2:
# 
# 
# Input: grid = [[3,5],[6,4]]
# 
# Output: 5
# 
# Explanation:
# 
# 
# Choose 5 from the first row and 4 from the second row.
# The bitwise OR of 5 | 4 = 5​​​​​​​, which is the minimum possible.
# 
# 
# 
# Example 3:
# 
# 
# Input: grid = [[7,9,8]]
# 
# Output: 7
# 
# Explanation:
# 
# 
# Choosing 7 gives the minimum bitwise OR.
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= m == grid.length <= 10^5
# 1 <= n == grid[i].length <= 10^5
# m * n <= 10^5
# 1 <= grid[i][j] <= 10^5​​​​​​​
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minimumOR(self, grid: List[List[int]]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given an `m x n` grid of positive integers.

        We must choose exactly one number from each row. After choosing one
        value per row, we compute the bitwise OR of all chosen values.

        Return the minimum possible OR value.

        Example:

            grid = [[1, 5],
                    [2, 4]]

            choose 1 from row 0 and 2 from row 1
            OR = 1 | 2 = 3

            answer = 3

        Important bitwise viewpoint
        ---------------------------
        The final answer is a bitmask.

        If the final OR mask is `mask`, then every selected number `x` must have
        only bits that are also present in `mask`.

        In code, `x` is allowed by `mask` when:

            (x | mask) == mask

        equivalently:

            (x & ~mask) == 0

        That means `x` does not contain any forbidden bit outside `mask`.

        Feasibility check
        -----------------
        A mask is feasible if we can choose one number from every row such that
        every chosen number fits inside that mask.

        Since choices from different rows only interact through the final OR
        mask, the feasibility condition is simple:

            for every row, there exists at least one value x with
            (x | mask) == mask

        If every row has at least one allowed value, choose one such value from
        each row and the final OR will be a submask of `mask`. Therefore the
        selected OR is at most `mask` in the bit sense and uses no forbidden
        bits.

        Monotonicity
        ------------
        Feasibility is monotone over masks:

        If `mask` is feasible, then any `larger_mask` that contains all bits of
        `mask` is also feasible.

        Why?
        All values that were allowed under `mask` are still allowed when we turn
        on more bits.

        This monotonicity lets us greedily decide bits from most significant to
        least significant.

        Greedy bit decision
        -------------------
        We want the smallest integer answer, so high bits matter first.

        Start with a mask containing all bits that could possibly appear:

            ans = 2^B - 1

        where `B` is enough to cover the largest grid value.

        Then try to turn off bits from high to low:

            candidate = ans with current bit cleared

        If `candidate` is still feasible, keep that bit off:

            ans = candidate

        Otherwise, that bit is necessary, so leave it on.

        Why high-to-low?
        The numeric value of a binary number is determined lexicographically by
        bits from most significant to least significant. If we can make a higher
        bit 0, that is always better than any choices about lower bits.

        Why this is not ordinary sorting or per-row minimum
        --------------------------------------------------
        Choosing the smallest number in each row is not always enough because OR
        cares about which bit positions are introduced, not only numeric size.

        Example:

            row 0: [3, 4]      # 3 = 011, 4 = 100
            row 1: [4]

        Picking row minima gives:

            3 | 4 = 7

        But choosing 4 from row 0 gives:

            4 | 4 = 4

        which is better. The algorithm must reason about bit compatibility, not
        individual numeric minima.

        Data structure choice
        ---------------------
        We do not need a graph, heap, trie, DP table, or set of all possible OR
        values.

        We only need:

        * `ans`: current best feasible mask
        * `candidate`: mask after trying to remove one bit
        * a helper `can(mask)` that scans rows

        The grid itself is the only collection we scan. This keeps memory usage
        constant beyond the input.

        Algorithm
        ---------
        1. Find the maximum value in the grid.
        2. Let `bits = max_value.bit_length()`.
        3. Initialize:

               ans = (1 << bits) - 1

           This mask has all possible relevant bits turned on, so every grid
           value is allowed by it.

        4. Define `can(mask)`:

               for each row:
                   if no value in the row is a submask of mask:
                       return False
               return True

        5. For each bit from `bits - 1` down to `0`:

               candidate = ans without this bit
               if can(candidate):
                   ans = candidate

        6. Return `ans`.

        Walkthrough
        -----------
        For:

            grid = [[3, 5],
                    [6, 4]]

        Values use 3 bits, so start:

            ans = 111b = 7

        Try clearing bit 2:

            candidate = 011b = 3

        Row 0 has 3 allowed, but row 1 has neither 6 nor 4 allowed under 3.
        So bit 2 must stay on.

        Try clearing bit 1:

            candidate = 101b = 5

        Row 0 has 3? no, 5? yes.
        Row 1 has 6? no, 4? yes.
        Feasible, so ans becomes 5.

        Try clearing bit 0:

            candidate = 100b = 4

        Row 0 has neither 3 nor 5 allowed under 4.
        Not feasible, so bit 0 stays on.

        Final answer:

            101b = 5

        Correctness proof
        -----------------
        Lemma 1:
        `can(mask)` returns True if and only if there exists a valid selection
        with final OR using only bits from `mask`.

        Proof:
        If `can(mask)` returns True, every row has at least one value whose bits
        are all contained in `mask`. Choose one such value from each row. The OR
        of those chosen values cannot contain any bit outside `mask`, so the
        selection is valid under `mask`.

        Conversely, if there exists a valid selection whose OR uses only bits
        from `mask`, then every selected value must also use only bits from
        `mask`. Therefore each row contains at least one allowed value, so
        `can(mask)` returns True.

        Lemma 2:
        Feasibility is monotone: if `can(mask)` is True and `supermask` contains
        every bit of `mask`, then `can(supermask)` is also True.

        Proof:
        Every value allowed by `mask` has no bits outside `mask`. Since all bits
        of `mask` are also present in `supermask`, the same value has no bits
        outside `supermask`. Thus each row's previous allowed choice remains
        allowed.

        Lemma 3:
        When the algorithm decides a bit, its choice is optimal among all masks
        sharing the already-decided higher bits.

        Proof:
        The algorithm processes bits from high to low. At a bit position, it
        first tries setting that bit to 0 while keeping the higher decisions
        already fixed. If the resulting candidate is feasible, then some valid
        answer exists with this bit 0, so choosing 0 is strictly better than
        choosing 1 at this position. If the candidate is infeasible, then by
        Lemma 2 no mask with the same higher bits and this bit 0 can be feasible,
        because such masks only differ by lower bits and are submasks of the
        failed candidate with respect to the current allowed high bits. Therefore
        the bit must remain 1.

        Lemma 4:
        After processing all bits, `ans` is the smallest feasible mask.

        Proof:
        By Lemma 3, each bit is chosen optimally given all more significant bit
        choices. Since integer order compares binary numbers from most
        significant bit to least significant bit, the final mask is the
        lexicographically smallest feasible bit pattern, which is exactly the
        numerically smallest feasible OR value.

        Theorem:
        The algorithm returns the minimum possible bitwise OR after choosing
        exactly one value from each row.

        Proof:
        By Lemma 1, feasible masks are exactly masks that can cover one valid
        choice from every row. By Lemma 4, the algorithm returns the smallest
        feasible mask. Therefore it returns the minimum possible final OR.

        Complexity analysis
        -------------------
        Let:

            T = total number of grid elements = m * n
            B = number of bits needed for the largest value

        Since `grid[i][j] <= 10^5`, `B <= 17`.

        Time:

            O(B * T)

        Reason:
        For each bit, `can(mask)` may scan every grid value once. With at most 17
        bits, this is effectively linear in the input size.

        Space:

            O(1)

        Reason:
        We store only a few integer variables and loop counters. The feasibility
        check scans the existing grid without building auxiliary arrays.

        Edge cases
        ----------
        * One row:
          We only choose one number, so the answer is simply the minimum value in
          that row. The bit-greedy feasibility check naturally finds it.

        * One column:
          We must choose every number, so the answer is the OR of the column.
          Each row has only one possible value, and feasibility enforces all its
          bits.

        * Identical rows or repeated values:
          Repetition does not change the logic. A row only needs at least one
          allowed value.

        * Large grid with many columns:
          The total number of elements is at most 100000, and each bit check is
          a linear scan.

        * Values sharing bits:
          The algorithm can choose a numerically larger value from a row if it
          shares already-needed bits and avoids introducing worse bits.

        Test strategy
        -------------
        Useful tests:

            [[1, 5], [2, 4]]       -> 3
            [[3, 5], [6, 4]]       -> 5
            [[7, 9, 8]]            -> 7
            [[3, 4], [4]]          -> 4
            [[1], [2], [4]]        -> 7
            [[8, 1], [8, 2], [8]]  -> 8

        For a small local brute-force test, enumerate one choice per row and
        compare the minimum OR against this greedy algorithm.

        Possible improvements
        ---------------------
        The asymptotic time is already optimal up to the small bit factor because
        every row may need to be inspected to prove feasibility.

        If `B` were much larger, we could precompute per-row bitsets or allowed
        masks, but for `10^5` values and at most 17 relevant bits, the direct
        scan is simpler and fast.
        """

        max_value = max(max(row) for row in grid)
        bits = max_value.bit_length()
        ans = (1 << bits) - 1

        def can(mask: int) -> bool:
            for row in grid:
                if not any((value | mask) == mask for value in row):
                    return False
            return True

        for bit in range(bits - 1, -1, -1):
            candidate = ans & ~(1 << bit)
            if can(candidate):
                ans = candidate

        return ans
# @lc code=end
