#
# @lc app=leetcode id=3857 lang=python3
#
# [3857] Minimum Cost to Split into Ones
#
# https://leetcode.com/problems/minimum-cost-to-split-into-ones/description/
#
# algorithms
# Medium (83.23%)
# Likes:    59
# Dislikes: 9
# Total Accepted:    48.6K
# Total Submissions: 58.4K
# Testcase Example:  '3'
#
# You are given an integer n.
# 
# In one operation, you may split an integer x into two positive integers a and
# b such that a + b = x.
# 
# The cost of this operation is a * b.
# 
# Return an integer denoting the minimum total cost required to split the
# integer n into n ones.
# 
# 
# Example 1:
# 
# 
# Input: n = 3
# 
# Output: 3
# 
# Explanation:
# 
# One optimal set of operations is:
# 
# 
# 
# 
# x
# a
# b
# a + b
# a * b
# Cost
# 
# 
# 3
# 1
# 2
# 3
# 2
# 2
# 
# 
# 2
# 1
# 1
# 2
# 1
# 1
# 
# 
# 
# 
# Thus, the minimum total cost is 2 + 1 = 3.
# 
# 
# Example 2:
# 
# 
# Input: n = 4
# 
# Output: 6
# 
# Explanation:
# 
# 
# One optimal set of operations is:
# 
# 
# 
# 
# x
# a
# b
# a + b
# a * b
# Cost
# 
# 
# 4
# 2
# 2
# 4
# 4
# 4
# 
# 
# 2
# 1
# 1
# 2
# 1
# 1
# 
# 
# 2
# 1
# 1
# 2
# 1
# 1
# 
# 
# 
# 
# Thus, the minimum total cost is 4 + 1 + 1 = 6.
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 500
# 
# 
#

# @lc code=start
class Solution:
    def minCost(self, n: int) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We start with one integer `n`.

        In one operation, we choose an integer `x` that currently exists and
        split it into two positive integers `a` and `b` such that:

            a + b = x

        The cost of that operation is:

            a * b

        We keep splitting until all pieces are `1`. Since the total sum stays
        `n`, the final state contains exactly `n` ones.

        Return the minimum total cost.

        Examples:

            n = 3

            split 3 -> 1 + 2, cost 1 * 2 = 2
            split 2 -> 1 + 1, cost 1 * 1 = 1

            total = 3

            n = 4

            split 4 -> 2 + 2, cost 4
            split 2 -> 1 + 1, cost 1
            split 2 -> 1 + 1, cost 1

            total = 6

        Key observation: the total cost is actually fixed
        -------------------------------------------------
        Although the problem asks for the minimum, every possible complete
        splitting strategy has the same total cost:

            n * (n - 1) / 2

        Why?
        Think of the final `n` ones as `n` individual unit items.

        At any moment, each current integer piece represents a group of some
        number of final ones. For example, a piece of value `5` represents a
        group containing 5 final unit items.

        When we split a piece of size `x` into sizes `a` and `b`, we are
        separating that group into two subgroups:

            left group size  = a
            right group size = b

        There are exactly:

            a * b

        pairs of final ones where one unit is in the left subgroup and the other
        unit is in the right subgroup.

        That is exactly the operation cost.

        Pair-count interpretation
        -------------------------
        Every unordered pair of final ones starts together in the original group
        of size `n`.

        Eventually, all final ones are separate, so each pair must be separated
        at some operation.

        A pair is charged exactly once:

        * before the split that separates them, both units are in the same piece
        * during that split, they move into different child pieces, contributing
          1 to the `a * b` cross-pair count
        * after that split, they are in different pieces forever and can never be
          charged again

        Therefore, the total cost over all operations equals the number of
        unordered pairs among `n` final ones:

            C(n, 2) = n * (n - 1) / 2

        Since all strategies have this same cost, it is automatically the
        minimum possible cost.

        Dynamic programming viewpoint
        -----------------------------
        If an interviewer expects a recurrence, we can define:

            f(x) = minimum cost to split x into ones

        If the first split is:

            x -> a + (x - a)

        then:

            f(x) = min over a:
                   a * (x - a) + f(a) + f(x - a)

        The closed form:

            f(x) = x * (x - 1) / 2

        satisfies the recurrence because:

            a * b + a(a - 1)/2 + b(b - 1)/2
            = (2ab + a^2 - a + b^2 - b) / 2
            = ((a + b)^2 - (a + b)) / 2
            = x(x - 1)/2

        where `b = x - a`.

        Notice the result is independent of `a`, which matches the pair-count
        invariant.

        Data structure choice
        ---------------------
        No data structure is needed.

        We do not need:

        * a priority queue to decide which piece to split next
        * dynamic programming array
        * recursion tree simulation
        * greedy strategy

        The pair-count invariant collapses the entire process into one formula.

        Algorithm
        ---------
        Return:

            n * (n - 1) // 2

        The `//` is integer division. The product is always even because one of
        `n` and `n - 1` is even.

        Correctness proof
        -----------------
        Lemma 1:
        In one split `x -> a + b`, the cost `a * b` equals the number of pairs
        of final ones separated by that split.

        Proof:
        The piece of value `x` represents `x` final ones. After the split, `a`
        of those final ones are in one child piece and `b` are in the other.
        Choosing one final one from the first child and one from the second child
        gives exactly `a * b` cross pairs. These are precisely the pairs
        separated by this split.

        Lemma 2:
        Every pair of final ones is separated exactly once during the whole
        process.

        Proof:
        Initially, all final ones belong to the original piece `n`, so every
        pair starts together. At the end, every piece is a single one, so every
        pair ends separated. Consider any fixed pair. There is a first operation
        where the two units are no longer in the same piece. That operation
        separates the pair. After that, operations only split existing pieces;
        pieces are never merged, so the two units can never be together again.
        Thus the pair is separated exactly once.

        Lemma 3:
        The total cost of any complete splitting process is `C(n, 2)`.

        Proof:
        By Lemma 1, each operation cost counts exactly the number of final-one
        pairs separated in that operation. By Lemma 2, every unordered pair of
        final ones is counted exactly once across all operations. Therefore the
        total cost is the number of unordered pairs among `n` items:

            C(n, 2) = n * (n - 1) / 2

        Theorem:
        The algorithm returns the minimum total cost required to split `n` into
        ones.

        Proof:
        Lemma 3 shows that every valid complete splitting process has total cost
        `n * (n - 1) / 2`. Since every strategy has the same cost, that value is
        both achievable and minimal. The algorithm returns exactly that value.

        Complexity analysis
        -------------------
        Time:

            O(1)

        Reason:
        The algorithm performs a constant number of arithmetic operations.

        Space:

            O(1)

        Reason:
        The algorithm stores no data structure whose size depends on `n`.

        Edge cases
        ----------
        * `n = 1`:
          Already all ones. Formula gives `1 * 0 // 2 = 0`.

        * `n = 2`:
          One split: `2 -> 1 + 1`, cost `1`. Formula gives `2 * 1 // 2 = 1`.

        * Odd `n`:
          Example `n = 5`, answer is `10`. Integer division is safe because
          `5 * 4` is even.

        * Maximum constraint `n = 500`:
          Answer is `500 * 499 // 2 = 124750`, which easily fits in normal
          integer ranges.

        Test strategy
        -------------
        Useful tests:

            n = 1 -> 0
            n = 2 -> 1
            n = 3 -> 3
            n = 4 -> 6
            n = 5 -> 10
            n = 500 -> 124750

        For extra confidence, we can brute-force the DP recurrence for small
        values:

            dp[x] = min(a * (x - a) + dp[a] + dp[x - a])

        and compare it to `x * (x - 1) // 2`.

        Possible improvements
        ---------------------
        The formula is already optimal. A DP solution would be O(n^2) and useful
        only as a derivation or verification tool, not as the final solution.
        """

        return n * (n - 1) // 2
# @lc code=end
