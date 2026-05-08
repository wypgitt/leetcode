// Translated from 411.minimum-unique-word-abbreviation.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=411 lang=python3
// #
// # [411] Minimum Unique Word Abbreviation
// #
// # https://leetcode.com/problems/minimum-unique-word-abbreviation/description/
// #
// # algorithms
// # Hard (40.51%)
// # Likes:    185
// # Dislikes: 146
// # Total Accepted:    15.8K
// # Total Submissions: 38.9K
// # Testcase Example:  '"apple"\n["blade"]'
// #
// # A string can be abbreviated by replacing any number of non-adjacent
// # substrings with their lengths. For example, a string such as "substitution"
// # could be abbreviated as (but not limited to):
// # 
// # 
// # "s10n" ("s ubstitutio n")
// # "sub4u4" ("sub stit u tion")
// # "12" ("substitution")
// # "su3i1u2on" ("su bst i t u ti on")
// # "substitution" (no substrings replaced)
// # 
// # 
// # Note that "s55n" ("s ubsti tutio n") is not a valid abbreviation of
// # "substitution" because the replaced substrings are adjacent.
// # 
// # The length of an abbreviation is the number of letters that were not replaced
// # plus the number of substrings that were replaced. For example, the
// # abbreviation "s10n" has a length of 3 (2 letters + 1 substring) and
// # "su3i1u2on" has a length of 9 (6 letters + 3 substrings).
// # 
// # Given a target string target and an array of strings dictionary, return an
// # abbreviation of target with the shortest possible length such that it is not
// # an abbreviation of any string in dictionary. If there are multiple shortest
// # abbreviations, return any of them.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: target = "apple", dictionary = ["blade"]
// # Output: "a4"
// # Explanation: The shortest abbreviation of "apple" is "5", but this is also an
// # abbreviation of "blade".
// # The next shortest abbreviations are "a4" and "4e". "4e" is an abbreviation of
// # blade while "a4" is not.
// # Hence, return "a4".
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: target = "apple", dictionary = ["blade","plain","amber"]
// # Output: "1p3"
// # Explanation: "5" is an abbreviation of both "apple" but also every word in
// # the dictionary.
// # "a4" is an abbreviation of "apple" but also "amber".
// # "4e" is an abbreviation of "apple" but also "blade".
// # "1p3", "2p2", and "3l1" are the next shortest abbreviations of "apple".
// # Since none of them are abbreviations of words in the dictionary, returning
// # any of them is correct.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # m == target.length
// # n == dictionary.length
// # 1 <= m <= 21
// # 0 <= n <= 1000
// # 1 <= dictionary[i].length <= 100
// # log2(n) + m <= 21 if n > 0
// # target and dictionary[i] consist of lowercase English letters.
// # dictionary does not contain target.
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minAbbreviation(self, target: str, dictionary: List[str]) -> str:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We need abbreviate `target` as shortly as possible so that the
//         abbreviation does NOT match any word in `dictionary`.
// 
//         An abbreviation keeps some letters and replaces runs of skipped letters
//         with their run length.
// 
//         Example:
// 
//             target = "apple"
// 
//             keep positions 0 only:
//                 "a" + skip "pple" -> "a4"
// 
//             keep position 1 only:
//                 skip "a" + "p" + skip "ple" -> "1p3"
// 
//         If several shortest valid abbreviations exist, any one may be returned.
// 
//         Key observation 1: ignore dictionary words with different length
//         ---------------------------------------------------------------
//         Any abbreviation of `target` represents a word of length
//         `len(target)`.  It cannot also represent a dictionary word of a different
//         length.
// 
//         So only dictionary words with the same length as `target` matter.
// 
//         If there are none, the shortest abbreviation is just:
// 
//             str(len(target))
// 
//         which abbreviates the whole word.
// 
//         Key observation 2: represent an abbreviation by a bitmask
//         --------------------------------------------------------
//         Let:
// 
//             m = len(target)
// 
//         Use a bitmask with `m` bits:
// 
//         * bit i = 1 means keep `target[i]` as a literal letter
//         * bit i = 0 means abbreviate that position as part of a number block
// 
//         Example for "apple":
// 
//             mask 00001 keeps only index 0 -> "a4"
//             mask 00010 keeps only index 1 -> "1p3"
//             mask 11111 keeps all letters  -> "apple"
// 
//         Key observation 3: when does an abbreviation conflict?
//         -----------------------------------------------------
//         Consider a dictionary word `word` with the same length as `target`.
// 
//         If our abbreviation keeps a position where:
// 
//             target[i] != word[i]
// 
//         then the abbreviation cannot match `word`, because that literal letter
//         would be different.
// 
//         If every kept position has the same character in both strings, then the
//         abbreviation still matches `word`.
// 
//         Therefore, for each dictionary word, build a difference mask:
// 
//             diff[word] has bit i = 1 if target[i] != word[i]
// 
//         Our abbreviation mask distinguishes this word exactly when:
// 
//             abbreviation_mask & diff[word] != 0
// 
//         In words: we kept at least one position where the two words differ.
// 
//         The problem becomes
//         -------------------
//         Find a mask with minimum abbreviation length such that:
// 
//             for every diff mask:
//                 mask & diff != 0
// 
//         This is a small hitting-set problem over at most 21 positions.
// 
//         Why brute-force masks is acceptable
//         -----------------------------------
//         `m <= 21`, so there are at most:
// 
//             2^21 = 2,097,152
// 
//         masks.
// 
//         Also, the constraint says:
// 
//             log2(dictionary.length) + m <= 21
// 
//         when the dictionary is non-empty.  This keeps the product of candidate
//         masks and relevant dictionary checks small enough for direct search.
// 
//         Abbreviation length from a mask
//         -------------------------------
//         The problem defines abbreviation length as:
// 
//             number of kept letters + number of abbreviated substrings
// 
//         So a consecutive run of skipped positions counts as 1, regardless of
//         whether the run length is one digit or many digits.
// 
//         Example:
// 
//             mask for "substitution" that produces "s10n"
// 
//             kept letters: s, n -> 2
//             number block: 10  -> 1
//             length = 3
// 
//         For a mask:
// 
//         * each 1 bit contributes one kept letter
//         * each run of 0 bits contributes one number block
// 
//         Algorithm
//         ---------
//         1. Filter dictionary to words with length equal to `target`.
//         2. If the filtered list is empty, return `str(len(target))`.
//         3. Build one difference mask per relevant dictionary word.
//         4. Enumerate every possible abbreviation mask from `0` to `2^m - 1`.
//         5. Compute its abbreviation length.
//         6. Skip it if it is already no better than the best found.
//         7. Check whether it distinguishes every dictionary word:
// 
//                all(mask & diff for diff in diffs)
// 
//         8. Keep the best mask.
//         9. Convert the best mask into the actual abbreviation string.
// 
//         Data structure choice
//         ---------------------
//         We use integers as bitmasks.
// 
//         Why bitmasks fit perfectly:
// 
//         * `m <= 21`, so all positions fit comfortably in an integer.
//         * testing whether a kept position hits a difference mask is one fast
//           bitwise AND.
//         * enumerating candidate masks is simple and deterministic.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For a same-length dictionary word, an abbreviation mask is
//         unique against that word if and only if `mask & diff != 0`.
//         If `mask & diff != 0`, then the abbreviation keeps at least one position
//         where `target` and the dictionary word have different letters, so the
//         abbreviation cannot match that word.  If `mask & diff == 0`, every kept
//         letter is identical in both words, and skipped positions reveal no
//         character information, so the abbreviation also matches that word.
// 
//         Lemma 2: A mask is valid if and only if it satisfies
//         `mask & diff != 0` for every relevant dictionary word.
//         By Lemma 1, this condition is exactly what prevents the abbreviation
//         from matching each same-length dictionary word.  Different-length words
//         cannot match any abbreviation of `target`, so no other words matter.
// 
//         Lemma 3: The algorithm checks every possible abbreviation of `target`.
//         Every abbreviation is determined by exactly the set of positions kept as
//         letters, and every such set corresponds to exactly one mask from
//         `0` to `2^m - 1`.  The algorithm enumerates all of them.
// 
//         Lemma 4: `abbreviation_length(mask)` computes the length required by the
//         problem.
//         The function adds one for every kept letter and one for every maximal
//         consecutive run of skipped positions.  This exactly matches the rule:
//         letters count individually and each replaced substring counts once.
// 
//         Theorem: The algorithm returns a shortest valid abbreviation.
//         By Lemma 3, every possible abbreviation mask is considered.  By Lemma 2,
//         the algorithm correctly identifies which masks are valid.  By Lemma 4,
//         it compares masks using the required abbreviation length.  Therefore the
//         best mask selected by the algorithm has minimum possible length, and the
//         returned string is a shortest valid abbreviation.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             m = len(target), at most 21
//             d = number of dictionary words with length m
// 
//         There are `2^m` masks.  For each mask, computing abbreviation length
//         costs O(m), and checking validity costs O(d).
// 
//         Total time:
// 
//             O(2^m * (m + d))
// 
//         Under the problem's constraint `log2(n) + m <= 21`, this is feasible.
// 
//         Space:
// 
//             O(d)
// 
//         for the difference masks, excluding the output string.
// 
//         Edge cases
//         ----------
//         * Empty dictionary:
//           Return the full-length abbreviation, e.g. `"5"`.
// 
//         * No same-length dictionary words:
//           Same result, because different lengths cannot conflict.
// 
//         * The shortest abbreviation is the full target:
//           The all-ones mask is always valid because dictionary does not contain
//           `target`, so a solution always exists.
// 
//         * Multiple shortest answers:
//           The problem allows returning any of them.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               target = "apple", dictionary = ["blade"] -> "a4" or another
//               valid shortest abbreviation
// 
//               target = "apple", dictionary = ["blade","plain","amber"] ->
//               one of "1p3", "2p2", "3l1"
// 
//         * Empty dictionary.
//         * Dictionary words of different lengths only.
//         * Cases where the answer is the full word.
//         * Random small cases checked by brute-force abbreviation generation.
// 
//         Possible improvement?
//         ---------------------
//         We can search masks in increasing abbreviation length or use DFS with
//         pruning to avoid checking every mask.  That can be faster on some
//         inputs, but the direct bitmask search is concise, robust, and fits the
//         special constraints of this problem well.
//         """
// 
//         word_length = len(target)
//         relevant_words = [word for word in dictionary if len(word) == word_length]
// 
//         if not relevant_words:
//             return str(word_length)
// 
//         difference_masks: list[int] = []
//         for word in relevant_words:
//             difference = 0
// 
//             for index, (target_char, word_char) in enumerate(zip(target, word)):
//                 if target_char != word_char:
//                     difference |= 1 << index
// 
//             difference_masks.append(difference)
// 
//         def abbreviation_length(mask: int) -> int:
//             length = 0
//             index = 0
// 
//             while index < word_length:
//                 if mask & (1 << index):
//                     length += 1
//                     index += 1
//                 else:
//                     length += 1
//                     while index < word_length and not (mask & (1 << index)):
//                         index += 1
// 
//             return length
// 
//         def build_abbreviation(mask: int) -> str:
//             parts: list[str] = []
//             abbreviated_count = 0
// 
//             for index, character in enumerate(target):
//                 if mask & (1 << index):
//                     if abbreviated_count:
//                         parts.append(str(abbreviated_count))
//                         abbreviated_count = 0
//                     parts.append(character)
//                 else:
//                     abbreviated_count += 1
// 
//             if abbreviated_count:
//                 parts.append(str(abbreviated_count))
// 
//             return "".join(parts)
// 
//         best_mask = (1 << word_length) - 1
//         best_length = word_length
// 
//         for mask in range(1 << word_length):
//             current_length = abbreviation_length(mask)
//             if current_length >= best_length:
//                 continue
// 
//             if all(mask & difference for difference in difference_masks):
//                 best_mask = mask
//                 best_length = current_length
// 
//         return build_abbreviation(best_mask)
// # @lc code=end

#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
    int abbrLen(int mask, int n) {
        int len = 0, i = 0;
        while (i < n) {
            ++len;
            if (mask & (1 << i)) ++i;
            else while (i < n && !(mask & (1 << i))) ++i;
        }
        return len;
    }

    string build(string& target, int mask) {
        string ans;
        int cnt = 0;
        for (int i = 0; i < (int)target.size(); ++i) {
            if (mask & (1 << i)) {
                if (cnt) ans += to_string(cnt), cnt = 0;
                ans.push_back(target[i]);
            } else {
                ++cnt;
            }
        }
        if (cnt) ans += to_string(cnt);
        return ans;
    }

public:
    string minAbbreviation(string target, vector<string>& dictionary) {
        int n = target.size();
        vector<int> diffs;
        for (auto& w : dictionary) if ((int)w.size() == n) {
            int d = 0;
            for (int i = 0; i < n; ++i) if (target[i] != w[i]) d |= 1 << i;
            diffs.push_back(d);
        }
        if (diffs.empty()) return to_string(n);
        int bestMask = (1 << n) - 1, bestLen = n;
        for (int mask = 0; mask < (1 << n); ++mask) {
            int len = abbrLen(mask, n);
            if (len >= bestLen) continue;
            bool ok = true;
            for (int d : diffs) if ((mask & d) == 0) { ok = false; break; }
            if (ok) bestMask = mask, bestLen = len;
        }
        return build(target, bestMask);
    }
};
