#
# @lc app=leetcode id=3777 lang=python3
#
# [3777] Minimum Deletions to Make Alternating Substring
#
# https://leetcode.com/problems/minimum-deletions-to-make-alternating-substring/description/
#
# algorithms
# Hard (45.12%)
# Likes:    52
# Dislikes: 1
# Total Accepted:    6K
# Total Submissions: 13.4K
# Testcase Example:  '"ABA"\n[[2,1,2],[1,1],[2,0,2]]'
#
# You are given a string s of length n consisting only of the characters 'A'
# and 'B'.
# 
# You are also given a 2D integer array queries of length q, where each
# queries[i] is one of the following:
# 
# 
# [1, j]: Flip the character at index j of s i.e. 'A' changes to 'B' (and vice
# versa). This operation mutates s and affects subsequent queries.
# [2, l, r]: Compute the minimum number of character deletions required to make
# the substring s[l..r] alternating. This operation does not modify s; the
# length of s remains n.
# 
# 
# A substring is alternating if no two adjacent characters are equal. A
# substring of length 1 is always alternating.
# 
# Return an integer array answer, where answer[i] is the result of the i^th
# query of type [2, l, r].
# 
# 
# Example 1:
# 
# 
# Input: s = "ABA", queries = [[2,1,2],[1,1],[2,0,2]]
# 
# Output: [0,2]
# 
# Explanation:
# 
# 
# 
# 
# i
# queries[i]
# j
# l
# r
# s before query
# s[l..r]
# Result
# Answer
# 
# 
# 
# 
# 0
# [2, 1, 2]
# -
# 1
# 2
# "ABA"
# "BA"
# Already alternating
# 0
# 
# 
# 1
# [1, 1]
# 1
# -
# -
# "ABA"
# -
# Flip s[1] from 'B' to 'A'
# -
# 
# 
# 2
# [2, 0, 2]
# -
# 0
# 2
# "AAA"
# "AAA"
# Delete any two 'A's to get "A"
# 2
# 
# 
# 
# 
# Thus, the answer is [0, 2].
# 
# 
# Example 2:
# 
# 
# Input: s = "ABB", queries = [[2,0,2],[1,2],[2,0,2]]
# 
# Output: [1,0]
# 
# Explanation:
# 
# 
# 
# 
# i
# queries[i]
# j
# l
# r
# s before query
# s[l..r]
# Result
# Answer
# 
# 
# 
# 
# 0
# [2, 0, 2]
# -
# 0
# 2
# "ABB"
# "ABB"
# Delete one 'B' to get "AB"
# 1
# 
# 
# 1
# [1, 2]
# 2
# -
# -
# "ABB"
# -
# Flip s[2] from 'B' to 'A'
# -
# 
# 
# 2
# [2, 0, 2]
# -
# 0
# 2
# "ABA"
# "ABA"
# Already alternating
# 0
# 
# 
# 
# 
# Thus, the answer is [1, 0].
# 
# 
# Example 3:
# 
# 
# Input: s = "BABA", queries = [[2,0,3],[1,1],[2,1,3]]
# 
# Output: [0,1]
# 
# Explanation:
# 
# 
# 
# 
# i
# queries[i]
# j
# l
# r
# s before query
# s[l..r]
# Result
# Answer
# 
# 
# 
# 
# 0
# [2, 0, 3]
# -
# 0
# 3
# "BABA"
# "BABA"
# Already alternating
# 0
# 
# 
# 1
# [1, 1]
# 1
# -
# -
# "BABA"
# -
# Flip s[1] from 'A' to 'B'
# -
# 
# 
# 2
# [2, 1, 3]
# -
# 1
# 3
# "BBBA"
# "BBA"
# Delete one 'B' to get "BA"
# 1
# 
# 
# 
# 
# Thus, the answer is [0, 1].
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n == s.length <= 10^5
# s[i] is either 'A' or 'B'.
# 1 <= q == queries.length <= 10^5
# queries[i].length == 2 or 3
# 
# queries[i] == [1, j] or,
# queries[i] == [2, l, r]
# 0 <= j <= n - 1
# 0 <= l <= r <= n - 1
# 
# 
# 
# 
#

# @lc code=start
from typing import List


class FenwickTree:
    def __init__(self, size: int):
        self.size = size
        self.tree = [0] * (size + 1)

    def add(self, index: int, delta: int) -> None:
        index += 1
        while index <= self.size:
            self.tree[index] += delta
            index += index & -index

    def prefix_sum(self, index: int) -> int:
        total = 0
        index += 1
        while index > 0:
            total += self.tree[index]
            index -= index & -index
        return total

    def range_sum(self, left: int, right: int) -> int:
        if left > right:
            return 0
        return self.prefix_sum(right) - (
            self.prefix_sum(left - 1) if left > 0 else 0
        )


class Solution:
    def minDeletions(self, s: str, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We have a binary string `s` containing only `A` and `B`.

        There are two kinds of queries:

        * `[1, j]`:
          Flip `s[j]`.

        * `[2, l, r]`:
          For substring `s[l..r]`, return the minimum number of character
          deletions needed so the remaining string is alternating.

        A string is alternating if no two adjacent remaining characters are
        equal.

        Key reduction
        -------------
        For a binary string, the longest alternating subsequence is obtained by
        taking one character from each run of equal characters.

        Example:

            s = "AAABBBAA"

        Runs:

            "AAA", "BBB", "AA"

        We can keep one from each run:

            "ABA"

        and we cannot keep more than one character from the same run next to
        each other, because equal adjacent kept characters would violate
        alternation.

        Therefore:

            longest_alternating_subsequence_length = number_of_runs

        and:

            minimum_deletions = substring_length - number_of_runs

        Counting runs with adjacent transitions
        ---------------------------------------
        A new run starts exactly when adjacent characters differ.

        For substring `s[l..r]`:

            number_of_runs = 1 + number of i in [l, r - 1]
                                  where s[i] != s[i + 1]

        So the query answer is:

            length - (1 + transitions)

        where:

            length = r - l + 1
            transitions = count of adjacent unequal pairs inside s[l..r]

        Data structure choice
        ---------------------
        We need:

        * point updates after flipping one character
        * range sum queries over adjacent transition indicators

        Define an edge array:

            diff[i] = 1 if s[i] != s[i + 1], else 0

        for `0 <= i < n - 1`.

        A flip at index `j` can only affect:

            diff[j - 1]
            diff[j]

        because only adjacent pairs touching `j` can change.

        A type-2 query `[l, r]` needs:

            sum(diff[l..r - 1])

        This is exactly what a Fenwick tree supports:

        * update one `diff` position in O(log n)
        * query a range sum in O(log n)

        Algorithm
        ---------
        1. Convert `s` to a mutable list of characters.
        2. Build `diff` for all adjacent pairs.
        3. Insert `diff` into a Fenwick tree.
        4. For each query:
              * If it is a flip:
                    - remember old affected `diff` values around `j`
                    - flip `s[j]`
                    - recompute affected `diff` values
                    - update the Fenwick tree by the delta

              * If it is a range query:
                    - get transitions = sum(diff[l..r - 1])
                    - runs = transitions + 1
                    - answer = (r - l + 1) - runs

        Correctness proof
        -----------------
        Lemma 1: For any binary substring, the length of its longest alternating
        subsequence equals its number of runs.
        We can always choose one character from each run, and adjacent chosen
        characters come from different runs, so they alternate.  We cannot choose
        two characters from the same run with no different run between them,
        because they would be equal adjacent characters in the subsequence.
        Therefore the maximum length is exactly the number of runs.

        Lemma 2: For substring `s[l..r]`, the number of runs is
        `1 + sum(diff[l..r - 1])`.
        The first character starts the first run.  Each adjacent unequal pair
        starts exactly one new run, and adjacent equal pairs do not.

        Lemma 3: After every flip query, the Fenwick tree stores the correct
        `diff` array.
        Flipping `s[j]` can only change adjacent comparisons involving index
        `j`, namely `diff[j - 1]` and `diff[j]`.  The algorithm recomputes
        exactly those valid positions and applies their deltas to the tree, so
        all stored values remain correct.

        Theorem: Every type-2 query returns the minimum deletions needed to make
        `s[l..r]` alternating.
        By Lemma 3, the Fenwick tree returns the correct transition count.  By
        Lemma 2, this gives the correct number of runs.  By Lemma 1, the longest
        alternating subsequence has that many characters.  Deleting all other
        characters is necessary and sufficient, so the returned value is the
        minimum number of deletions.

        Complexity analysis
        -------------------
        Let:

            n = len(s)
            q = len(queries)

        Building the Fenwick tree:

            O(n log n)

        Each query:

            O(log n)

        Total time:

            O((n + q) log n)

        Space:

            O(n)

        for the mutable string and Fenwick tree.

        Edge cases
        ----------
        * n = 1:
          There are no adjacent edges.  Every substring has length 1, so every
          type-2 answer is 0.

        * l == r:
          The substring length is 1.  The transition range is empty, so answer
          is 0.

        * Already alternating substring:
          Every adjacent pair differs, so runs equals length and deletions is 0.

        * All equal substring:
          There is one run, so deletions is length - 1.

        * Repeated flips at the same index:
          Only local `diff` edges are updated each time.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              "ABA", [[2,1,2],[1,1],[2,0,2]] -> [0,2]
              "ABB", [[2,0,2],[1,2],[2,0,2]] -> [1,0]
              "BABA", [[2,0,3],[1,1],[2,1,3]] -> [0,1]

        * Single-character string.
        * Query with `l == r`.
        * Full all-equal string.
        * Small randomized cases compared with brute force.

        Possible improvement
        --------------------
        A segment tree would also work, but it is unnecessary because every
        range query only asks for a sum and every update is point-local.  Fenwick
        tree is simpler and has smaller constants.
        """

        chars = list(s)
        n = len(chars)
        fenwick = FenwickTree(max(1, n - 1))

        def edge_value(index: int) -> int:
            return 1 if chars[index] != chars[index + 1] else 0

        for index in range(n - 1):
            if edge_value(index):
                fenwick.add(index, 1)

        def refresh_edge(index: int, old_value: int) -> None:
            if 0 <= index < n - 1:
                new_value = edge_value(index)
                if new_value != old_value:
                    fenwick.add(index, new_value - old_value)

        answer = []

        for query in queries:
            if query[0] == 1:
                index = query[1]
                left_old = edge_value(index - 1) if index > 0 else 0
                right_old = edge_value(index) if index < n - 1 else 0

                chars[index] = 'B' if chars[index] == 'A' else 'A'

                refresh_edge(index - 1, left_old)
                refresh_edge(index, right_old)
            else:
                left, right = query[1], query[2]
                transitions = fenwick.range_sum(left, right - 1)
                length = right - left + 1
                runs = transitions + 1
                answer.append(length - runs)

        return answer
# @lc code=end


if __name__ == "__main__":
    def brute_force_min_deletions(substring: str) -> int:
        if not substring:
            return 0

        runs = 1
        for index in range(1, len(substring)):
            if substring[index] != substring[index - 1]:
                runs += 1

        return len(substring) - runs

    def brute_force_process(test_s: str, test_queries: List[List[int]]) -> List[int]:
        chars = list(test_s)
        result = []

        for query in test_queries:
            if query[0] == 1:
                index = query[1]
                chars[index] = 'B' if chars[index] == 'A' else 'A'
            else:
                left, right = query[1], query[2]
                result.append(brute_force_min_deletions("".join(chars[left:right + 1])))

        return result

    solution = Solution()

    fixed_tests = [
        ("ABA", [[2, 1, 2], [1, 1], [2, 0, 2]], [0, 2]),
        ("ABB", [[2, 0, 2], [1, 2], [2, 0, 2]], [1, 0]),
        ("BABA", [[2, 0, 3], [1, 1], [2, 1, 3]], [0, 1]),
        ("A", [[2, 0, 0], [1, 0], [2, 0, 0]], [0, 0]),
        ("AAAA", [[2, 0, 3], [1, 1], [2, 0, 3]], [3, 1]),
    ]

    for test_s, test_queries, expected in fixed_tests:
        assert solution.minDeletions(test_s, test_queries) == expected

    brute_force_cases = [
        ("AABBA", [[2, 0, 4], [1, 2], [2, 1, 3], [1, 0], [2, 0, 4]]),
        ("ABABAB", [[2, 0, 5], [1, 3], [2, 0, 5], [2, 2, 2]]),
        ("BBBBB", [[2, 0, 4], [1, 2], [2, 0, 4], [1, 1], [2, 1, 3]]),
    ]

    for test_s, test_queries in brute_force_cases:
        expected = brute_force_process(test_s, test_queries)
        assert solution.minDeletions(test_s, test_queries) == expected
