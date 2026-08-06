#
# @lc app=leetcode id=3863 lang=python3
#
# [3863] Minimum Operations to Sort a String
#
# https://leetcode.com/problems/minimum-operations-to-sort-a-string/description/
#
# algorithms
# Medium (18.87%)
# Likes:    98
# Dislikes: 10
# Total Accepted:    17.1K
# Total Submissions: 90.9K
# Testcase Example:  '"dog"'
#
# You are given a string s consisting of lowercase English letters.
# 
# In one operation, you can select any substring of s that is not the entire
# string and sort it in non-descending alphabetical order.
# 
# Return the minimum number of operations required to make s sorted in
# non-descending order. If it is not possible, return -1.
# 
# 
# Example 1:
# 
# 
# Input: s = "dog"
# 
# Output: 1
# 
# Explanation:​​​​​​​
# 
# 
# Sort substring "og" to "go".
# Now, s = "dgo", which is sorted in ascending order. Thus, the answer is 1.
# 
# 
# 
# Example 2:
# 
# 
# Input: s = "card"
# 
# Output: 2
# 
# Explanation:
# 
# 
# Sort substring "car" to "acr", so s = "acrd".
# Sort substring "rd" to "dr", making s = "acdr", which is sorted in ascending
# order. Thus, the answer is 2.
# 
# 
# 
# Example 3:
# 
# 
# Input: s = "gf"
# 
# Output: -1
# 
# Explanation:
# 
# 
# It is impossible to sort s under the given constraints. Thus, the answer is
# -1.
# 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# s consists of only lowercase English letters.
# 
# 
#

# @lc code=start
class Solution:
    def minOperations(self, s: str) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given a lowercase string `s`.

        In one operation, we may choose any substring that is NOT the entire
        string and sort that substring in non-descending alphabetical order.

        We need the minimum number of operations needed to make the whole string
        sorted in non-descending order. If it is impossible, return -1.

        Examples:

            "dog"  -> 1
            "card" -> 2
            "gf"   -> -1

        Key observation
        ---------------
        A single operation can sort either:

        * a prefix that excludes the last character
        * a suffix that excludes the first character
        * a middle substring that excludes both ends

        It can never sort the entire string in one operation.

        The only characters whose final positions are absolutely forced are:

        * the global minimum character must appear at the beginning area
        * the global maximum character must appear at the ending area

        More precisely:

        * If the first character is already a global minimum, then sorting the
          suffix `s[1:]` makes the whole string sorted.
        * If the last character is already a global maximum, then sorting the
          prefix `s[:-1]` makes the whole string sorted.

        Those give answer 1.

        Why answer can be at most 3 for n >= 3
        --------------------------------------
        If the string is unsorted and has at least 3 characters, there is always
        a way in at most 3 operations.

        Let:

            mn = min(s)
            mx = max(s)

        There are four main cases.

        Case 0: already sorted
        ----------------------
        If every adjacent pair satisfies:

            s[i - 1] <= s[i]

        then no operation is needed.

        Return 0.

        Case 1: length 2 and unsorted
        -----------------------------
        If `len(s) == 2` and the string is not sorted, the only substring that
        could change the order is the entire string, but that is forbidden.

        The only proper substrings have length 1, and sorting a one-character
        substring changes nothing.

        Return -1.

        Case 2: one operation is enough
        -------------------------------
        If:

            s[0] == mn

        then the first character can stay fixed. Sort the proper suffix
        `s[1:]`. Since every character in that suffix is at least `mn`, the
        whole string becomes sorted.

        If:

            s[-1] == mx

        then the last character can stay fixed. Sort the proper prefix `s[:-1]`.
        Since every character in that prefix is at most `mx`, the whole string
        becomes sorted.

        Return 1.

        Case 3: two operations are enough
        ---------------------------------
        We are now in the situation:

            s[0] != mn
            s[-1] != mx

        so one operation is not enough by the simple endpoint strategy above.

        If some middle character is a global minimum:

            mn occurs in s[1:-1]

        then:

        1. Sort the prefix ending at that middle minimum. This moves a minimum
           character to the first position.
        2. Sort the suffix starting at index 1. The first character is now a
           global minimum, so sorting the rest finishes the string.

        Symmetrically, if some middle character is a global maximum:

            mx occurs in s[1:-1]

        then:

        1. Sort the suffix starting at that middle maximum. This moves a maximum
           character to the last position.
        2. Sort the prefix ending at index n - 2. The last character is now a
           global maximum, so sorting the rest finishes the string.

        Return 2.

        Case 4: three operations are necessary and sufficient
        -----------------------------------------------------
        If none of the previous cases apply:

            s[0] != mn
            s[-1] != mx
            no middle character is mn
            no middle character is mx

        then all global maximum characters are forced to be at the first
        position, and all global minimum characters are forced to be at the last
        position.

        So the string has this endpoint problem:

            first char = global maximum
            last char  = global minimum

        Why at least 3?
        A proper substring cannot include both endpoints at the same time. To
        move the first maximum all the way to the last position, some operation
        must involve the last position. To move the last minimum all the way to
        the first position, some operation must involve the first position.

        With only two operations, one would have to fix one endpoint and the
        other would have to fix the other endpoint, but the character moved from
        one end cannot complete the full journey across both forbidden endpoints
        in only those two endpoint-limited operations.

        Why 3 is enough?
        Use this construction:

        1. Sort the prefix `s[:-1]`.
           The global maximum moves to index `n - 2`; the global minimum is
           still at the last index.

        2. Sort the suffix `s[1:]`.
           The global minimum moves to index 1; the global maximum moves to the
           last index.

        3. Sort the prefix `s[:-1]`.
           Now the maximum is already fixed at the end, and this final prefix
           sort arranges everything before it.

        Example:

            "zba"

            sort "zb" -> "bza"
            sort "za" -> "baz"
            sort "ba" -> "abz"

        Return 3.

        Data structure choice
        ---------------------
        We only need:

        * `n`: the string length
        * `mn`: the minimum character
        * `mx`: the maximum character
        * a scan over the middle substring

        No heap, stack, DP table, graph, or sorting of the whole string is
        needed.

        Why this is enough:

        The operation itself sorts substrings, but the minimum number of
        operations depends only on whether the global minimum or maximum is
        already at, or can quickly be moved to, a useful endpoint.

        Algorithm
        ---------
        1. If `s` is already sorted, return 0.
        2. If `len(s) == 2`, return -1.
        3. Compute `mn = min(s)` and `mx = max(s)`.
        4. If `s[0] == mn` or `s[-1] == mx`, return 1.
        5. If any middle character equals `mn` or `mx`, return 2.
        6. Otherwise, return 3.

        Correctness proof
        -----------------
        Lemma 1:
        If the string is already sorted, the algorithm returns the optimal
        answer 0.

        Proof:
        Zero operations are needed and no answer can be smaller than zero.

        Lemma 2:
        If an unsorted string has length 2, the answer is -1.

        Proof:
        The only proper substrings have length 1, and sorting a single character
        has no effect. Since the length-2 string starts unsorted and can never
        change, sorting it is impossible.

        Lemma 3:
        If `s[0] == mn` or `s[-1] == mx`, one operation is sufficient.

        Proof:
        If `s[0] == mn`, sort `s[1:]`. The suffix becomes sorted, and every
        suffix character is at least the first character, so the whole string is
        sorted. The suffix is a proper substring.

        If `s[-1] == mx`, sort `s[:-1]`. The prefix becomes sorted, and every
        prefix character is at most the last character, so the whole string is
        sorted. The prefix is a proper substring.

        Lemma 4:
        If a middle character is `mn` or `mx`, two operations are sufficient.

        Proof:
        If a middle character is `mn`, sort the prefix ending there. A global
        minimum moves to the first position. Then by Lemma 3's suffix argument,
        one more operation sorts the rest.

        If a middle character is `mx`, sort the suffix starting there. A global
        maximum moves to the last position. Then by Lemma 3's prefix argument,
        one more operation sorts the rest.

        Lemma 5:
        If no earlier case applies, three operations are sufficient.

        Proof:
        The construction described in Case 4 uses only proper substrings:
        prefix, suffix, prefix. After the second operation, the global maximum
        is fixed at the last position. The third operation sorts every character
        before it, producing a globally sorted string.

        Lemma 6:
        If no earlier case applies, fewer than three operations are not enough.

        Proof:
        In this case the global maximum is only at the first position and the
        global minimum is only at the last position. A proper substring cannot
        include both endpoints. Moving the first maximum to the last position
        requires an operation touching the last endpoint, and moving the last
        minimum to the first position requires an operation touching the first
        endpoint. Two operations cannot both carry both extreme characters all
        the way to their final opposite endpoints because each operation must
        exclude at least one endpoint. Therefore at least three operations are
        required.

        Theorem:
        The algorithm returns the minimum number of operations.

        Proof:
        The algorithm handles the sorted and impossible length-2 cases by
        Lemmas 1 and 2. It returns 1 only when Lemma 3 gives a valid one-step
        construction. It returns 2 only when Lemma 4 gives a valid two-step
        construction and the one-step case has already failed. In the remaining
        case, Lemmas 5 and 6 show that exactly 3 operations are necessary and
        sufficient. Thus every returned value is optimal.

        Complexity analysis
        -------------------
        Let `n = len(s)`.

        Time:

            O(n)

        Reason:
        We scan the string to check sortedness, find `min` and `max`, and scan
        the middle characters once. Each scan is linear.

        Space:

            O(1)

        Reason:
        We store only a few scalar variables. The alphabet size is fixed, and we
        do not allocate any data structure proportional to `n`.

        Edge cases
        ----------
        * Length 1:
          Always sorted, so return 0.

        * Length 2 sorted:
          Example: "fg" -> 0.

        * Length 2 unsorted:
          Example: "gf" -> -1.

        * Already sorted longer string:
          Example: "aabbcc" -> 0.

        * One operation because first is minimum:
          Example: "azby" -> sort "zby" into "byz" -> "abyz".

        * One operation because last is maximum:
          Example: "cbad" -> sort "cba" into "abc" -> "abcd".

        * Two operations because a middle minimum exists:
          Example: "zbaa" -> "abza" -> "aabz".

        * Three operations when maximum is trapped at the front and minimum is
          trapped at the back:
          Example: "zba" -> "bza" -> "baz" -> "abz".

        Test strategy
        -------------
        Useful tests:

            "dog"    -> 1
            "card"   -> 2
            "gf"     -> -1
            "a"      -> 0
            "ab"     -> 0
            "ba"     -> -1
            "aabb"   -> 0
            "azby"   -> 1
            "cbad"   -> 1
            "zbaa"   -> 2
            "zba"    -> 3
            "zyxa"   -> 3

        Possible improvements
        ---------------------
        We could compare `s == ''.join(sorted(s))` to check whether the string
        is already sorted, but that costs O(n log n) time and O(n) space.

        The adjacent-pair check keeps the whole algorithm O(n) time and O(1)
        extra space, which is optimal because we may need to inspect the input
        characters.
        """

        n = len(s)

        if all(s[i - 1] <= s[i] for i in range(1, n)):
            return 0

        if n == 2:
            return -1

        mn = min(s)
        mx = max(s)

        if s[0] == mn or s[-1] == mx:
            return 1

        if any(ch == mn or ch == mx for ch in s[1:-1]):
            return 2

        return 3
# @lc code=end
