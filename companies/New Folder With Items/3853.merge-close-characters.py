#
# @lc app=leetcode id=3853 lang=python3
#
# [3853] Merge Close Characters
#
# https://leetcode.com/problems/merge-close-characters/description/
#
# algorithms
# Medium (54.64%)
# Likes:    78
# Dislikes: 12
# Total Accepted:    28.5K
# Total Submissions: 52.2K
# Testcase Example:  '"abca"\n3'
#
# You are given a string s consisting of lowercase English letters and an
# integer k.
# 
# Two equal characters in the current string s are considered close if the
# distance between their indices is at most k.
# 
# When two characters are close, the right one merges into the left. Merges
# happen one at a time, and after each merge, the string updates until no more
# merges are possible.
# 
# Return the resulting string after performing all possible merges.
# 
# Note: If multiple merges are possible, always merge the pair with the
# smallest left index. If multiple pairs share the smallest left index, choose
# the pair with the smallest right index.
# 
# 
# Example 1:
# 
# 
# Input: s = "abca", k = 3
# 
# Output: "abc"
# 
# Explanation:
# 
# 
# ​​​​​​​Characters 'a' at indices i = 0 and i = 3 are close as 3 - 0 = 3 <=
# k.
# Merge them into the left 'a' and s = "abc".
# No other equal characters are close, so no further merges occur.
# 
# 
# 
# Example 2:
# 
# 
# Input: s = "aabca", k = 2
# 
# Output: "abca"
# 
# Explanation:
# 
# 
# Characters 'a' at indices i = 0 and i = 1 are close as 1 - 0 = 1 <= k.
# Merge them into the left 'a' and s = "abca".
# Now the remaining 'a' characters at indices i = 0 and i = 3 are not close as
# k < 3, so no further merges occur.
# 
# 
# 
# Example 3:
# 
# 
# Input: s = "yybyzybz", k = 2
# 
# Output: "ybzybz"
# 
# Explanation:
# 
# 
# Characters 'y' at indices i = 0 and i = 1 are close as 1 - 0 = 1 <= k.
# Merge them into the left 'y' and s = "ybyzybz".
# Now the characters 'y' at indices i = 0 and i = 2 are close as 2 - 0 = 2 <=
# k.
# Merge them into the left 'y' and s = "ybzybz".
# No other equal characters are close, so no further merges occur.
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 100
# 1 <= k <= s.length
# s consists of lowercase English letters.
# 
# 
#

# @lc code=start
class Solution:
    def mergeCharacters(self, s: str, k: int) -> str:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given a lowercase string `s` and an integer `k`.

        In the current string, two equal characters at indices `i < j` are
        considered close when:

            j - i <= k

        If two characters are close, the right character merges into the left
        one. In string terms, this means we delete the right character.

        Merges happen one at a time. After each merge, the string changes and all
        indices shift. We continue until no valid merge remains.

        Tie-breaking rule:

        1. Choose the valid pair with the smallest left index.
        2. If several pairs have that left index, choose the smallest right
           index.

        We must return the final string.

        Why direct simulation is the best fit
        -------------------------------------
        The constraints are small:

            len(s) <= 100

        Also, the problem defines an exact dynamic process with tie-breaking.
        The safest implementation is to simulate that process exactly:

        * scan `i` from left to right
        * for each `i`, scan `j` from `i + 1` up to `i + k`
        * the first equal pair found is exactly the pair required by the
          tie-breaking rule
        * delete `j`
        * restart scanning from the beginning because indices changed

        Restarting is important. After a deletion, characters that were farther
        right shift left and may become close to an earlier character.

        Example:

            s = "yybyzybz", k = 2

            current: "yybyzybz"
            first valid pair is (0, 1), delete index 1:

                "ybyzybz"

            restart. Now the two `y` characters are at indices 0 and 2, which
            are close, so delete index 2:

                "ybzybz"

            no more valid pair exists.

        Data structure choice
        ---------------------
        Strings are immutable in Python, so deleting a character from a string
        repeatedly would create a new string each time.

        We convert the string to a list of characters:

            chars = list(s)

        Why a list?

        * index access is simple
        * deleting `chars[j]` directly models "right merges into left"
        * at the end, `''.join(chars)` returns the final string

        Since `n <= 100`, list deletion cost is completely fine.

        Algorithm
        ---------
        1. Convert `s` to `chars`.
        2. Repeat:
              - set `merged = False`
              - scan every possible left index `i`
              - scan right index `j` from `i + 1` to `min(n - 1, i + k)`
              - if `chars[i] == chars[j]`, delete `chars[j]`, set
                `merged = True`, and stop the scan
        3. If a full scan finds no merge, stop.
        4. Return `''.join(chars)`.

        Correctness proof
        -----------------
        Lemma 1:
        During one scan, the first pair found by the nested loops is exactly the
        pair required by the tie-breaking rule.

        Proof:
        The outer loop visits left indices `i` in increasing order, so the first
        left index that has any valid merge is the smallest possible left index.
        For that fixed `i`, the inner loop visits right indices `j` in
        increasing order, so the first matching close character is the smallest
        possible right index for that left index. This matches the rule exactly.

        Lemma 2:
        When the algorithm deletes `chars[j]`, it performs the same merge as the
        problem statement.

        Proof:
        The problem says the right equal character merges into the left one.
        The left character remains, and the right character disappears. Deleting
        `chars[j]` keeps `chars[i]` and removes the right character, exactly
        modeling the merge.

        Lemma 3:
        After every iteration, the algorithm's `chars` list equals the current
        string that would result from following the problem's merge process for
        the same number of operations.

        Proof:
        Initially, `chars` is exactly `list(s)`. Assume it matches the current
        problem string before an iteration. By Lemma 1, the algorithm chooses the
        same pair the problem requires. By Lemma 2, it applies the same merge.
        Therefore, after the deletion, `chars` again matches the updated problem
        string.

        Lemma 4:
        The algorithm stops if and only if no possible merge remains.

        Proof:
        A full scan checks every left index and every right index within distance
        `k`. Therefore, if it finds no equal close pair, none exists. Conversely,
        if a valid merge exists, the nested loops will encounter one and perform
        a deletion, so the algorithm will not stop.

        Theorem:
        The algorithm returns the resulting string after performing all possible
        merges under the required tie-breaking rule.

        Proof:
        By Lemma 3, after each performed merge, the simulated string matches the
        problem process. By Lemma 4, the algorithm stops exactly when the process
        has no remaining merge. Therefore the joined `chars` string is exactly
        the required final result.

        Complexity analysis
        -------------------
        Let `n = len(s)`.

        Each successful merge deletes one character, so there are at most
        `n - 1` merges.

        For each merge attempt, the nested scan checks at most:

            O(n * min(k, n))

        pairs, which is `O(n^2)` in the worst case. Deleting from a list costs
        `O(n)`, which is dominated by the scan.

        Total time:

            O(n^3)

        With `n <= 100`, this is easily acceptable and keeps the code faithful to
        the statement.

        Space:

            O(n)

        for the mutable character list.

        Edge cases
        ----------
        * Length 1:
          No pair exists, return the original string.

        * No repeated characters:
          No merge ever happens.

        * All same characters:
          Repeatedly delete the nearest right duplicate according to the rule.

        * Large `k`:
          A left character can merge with any equal character to its right, but
          the smallest right index is still chosen first.

        * New closeness after deletion:
          Restarting the scan handles cases where a deletion shifts characters
          closer together.

        Test strategy
        -------------
        Useful tests:

            s = "abca",     k = 3 -> "abc"
            s = "aabca",    k = 2 -> "abca"
            s = "yybyzybz", k = 2 -> "ybzybz"
            s = "abc",      k = 2 -> "abc"
            s = "aaaa",     k = 1 -> "a"
            s = "ababa",    k = 2 -> "ab"

        For extra confidence, trace each deletion manually on short strings and
        verify that the chosen pair always has the smallest left index and then
        smallest right index.

        Possible improvements
        ---------------------
        For larger constraints, we could maintain positions of each character in
        ordered sets and use a priority queue of merge candidates. That would be
        more complex because every deletion changes indices. With `n <= 100`,
        direct simulation is clearer, less error-prone, and fast enough.
        """

        chars = list(s)

        while True:
            merged = False
            n = len(chars)

            for left in range(n):
                right_limit = min(n, left + k + 1)
                for right in range(left + 1, right_limit):
                    if chars[left] == chars[right]:
                        del chars[right]
                        merged = True
                        break
                if merged:
                    break

            if not merged:
                return "".join(chars)
# @lc code=end
