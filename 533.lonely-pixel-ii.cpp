/*
 * @lc app=leetcode id=533 lang=cpp
 *
 * [533] Lonely Pixel II
 */
// Translated from 533.lonely-pixel-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=533 lang=python3
// #
// # [533] Lonely Pixel II
// #
// # https://leetcode.com/problems/lonely-pixel-ii/description/
// #
// # algorithms
// # Medium (48.88%)
// # Likes:    93
// # Dislikes: 788
// # Total Accepted:    14.4K
// # Total Submissions: 29.5K
// # Testcase Example:  '[["W","B","W","B","B","W"],["W","B","W","B","B","W"],["W","B","W","B","B","W"],["W","W","B","W","B","W"]]\n' +
// # '3'
// #
// # Given an m x n picture consisting of black 'B' and white 'W' pixels and an
// # integer target, return the number of black lonely pixels.
// # 
// # A black lonely pixel is a character 'B' that located at a specific position
// # (r, c) where:
// # 
// # 
// # Row r and column c both contain exactly target black pixels.
// # For all rows that have a black pixel at column c, they should be exactly the
// # same as row r.
// # 
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: picture =
// # [["W","B","W","B","B","W"],["W","B","W","B","B","W"],["W","B","W","B","B","W"],["W","W","B","W","B","W"]],
// # target = 3
// # Output: 6
// # Explanation: All the green 'B' are the black pixels we need (all 'B's at
// # column 1 and 3).
// # Take 'B' at row r = 0 and column c = 1 as an example:
// # ⁠- Rule 1, row r = 0 and column c = 1 both have exactly target = 3 black
// # pixels. 
// # ⁠- Rule 2, the rows have black pixel at column c = 1 are row 0, row 1 and row
// # 2. They are exactly the same as row r = 0.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: picture = [["W","W","B"],["W","W","B"],["W","W","B"]], target = 1
// # Output: 0
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # m == picture.length
// # n == picture[i].length
// # 1 <= m, n <= 200
// # picture[i][j] is 'W' or 'B'.
// # 1 <= target <= min(m, n)
// # 
// # 
// #
// 
// # lc-original code=start
// from collections import Counter
// from typing import List
// 
// 
// class Solution:
//     def findBlackPixel(self, picture: List[List[str]], target: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given an `m x n` grid of:
// 
//             'B' = black pixel
//             'W' = white pixel
// 
//         A black pixel at `(r, c)` is counted if:
// 
//         1. Row `r` contains exactly `target` black pixels.
//         2. Column `c` contains exactly `target` black pixels.
//         3. Every row that has a black pixel in column `c` is exactly identical
//            to row `r`.
// 
//         We need count all black pixels satisfying these rules.
// 
//         Key observation
//         ---------------
//         Suppose row pattern `P` has exactly `target` black pixels and appears
//         exactly `target` times in the picture.
// 
//         If a column `c` has:
// 
//             P[c] == 'B'
// 
//         then those `target` identical rows each contribute a black pixel in
//         column `c`.
// 
//         If the total column count is also exactly `target`, then the only black
//         pixels in column `c` are from those identical rows.  That means every row
//         with a black pixel in column `c` is identical to `P`, exactly satisfying
//         rule 3.
// 
//         Therefore, we can count valid pixels by row pattern.
// 
//         Data structures
//         ---------------
//         * `row_count`
//           A Counter mapping each row pattern to how many times it appears.
//           We convert each row list into a string, e.g. `"WBWBBW"`, so it can be
//           used as a hash-map key.
// 
//         * `column_black_count`
//           A list where `column_black_count[c]` is the number of black pixels in
//           column `c`.
// 
//         These two structures give O(1)-style checks for the two expensive pieces
//         of information:
// 
//         * how often a row pattern appears
//         * how many black pixels a column has
// 
//         Algorithm
//         ---------
//         1. Count black pixels in each column.
//         2. Count each row pattern with `Counter`.
//         3. For every distinct row pattern:
//               - skip it unless it appears exactly `target` times
//               - skip it unless the row itself contains exactly `target` black
//                 pixels
//               - for every column where this row pattern has 'B':
//                     if the column also has exactly `target` black pixels,
//                     then all `target` occurrences of this row pattern contribute
//                     valid black pixels in this column
//         4. Return the total.
// 
//         Why add `target` per valid column?
//         ----------------------------------
//         If a row pattern appears exactly `target` times, and column `c` is valid
//         for that pattern, then each of those `target` rows has a black pixel at
//         column `c`.  All `target` of those pixels satisfy the rules, so the
//         contribution is `target`, not 1.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Any pixel counted by the algorithm satisfies all problem rules.
//         The algorithm only uses row patterns that contain exactly `target` black
//         pixels, so rule 1 holds.  It only counts columns whose total black count
//         is exactly `target`, so rule 2 holds.  The row pattern appears exactly
//         `target` times, and all those rows have 'B' in the counted column.  Since
//         the column has exactly `target` black pixels total, there cannot be any
//         other different row with 'B' in that column.  Thus every row with a black
//         pixel in the column is identical to the counted row pattern, so rule 3
//         holds.
// 
//         Lemma 2: Every valid black pixel is counted by the algorithm.
//         Consider a valid pixel `(r, c)` and let `P` be row `r`'s pattern.
//         Rule 1 says `P` has exactly `target` black pixels.  Rule 2 says column
//         `c` has exactly `target` black pixels.  Rule 3 says every row with 'B'
//         in column `c` is identical to `P`.  Since column `c` has exactly
//         `target` black pixels, exactly `target` rows with pattern `P` appear.
//         Therefore the algorithm processes pattern `P`, sees `P[c] == 'B'`, sees
//         the column count is `target`, and adds all `target` valid pixels in that
//         column, including `(r, c)`.
// 
//         Theorem: The algorithm returns exactly the number of black lonely pixels.
//         By Lemma 1, every counted pixel is valid.  By Lemma 2, every valid pixel
//         is counted.  Therefore the returned total is exactly correct.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             m = number of rows
//             n = number of columns
// 
//         Counting columns scans the grid once: O(mn).
//         Building row patterns and counting them also costs O(mn).
//         Processing distinct row patterns costs at most O(mn) total because there
//         are at most m patterns and each pattern has length n.
// 
//         Total time:  O(mn)
//         Total space: O(mn)
// 
//         The space is mainly for storing row-pattern strings in the Counter.
// 
//         Edge cases
//         ----------
//         * No row has exactly `target` black pixels:
//           Answer is 0.
// 
//         * A column has exactly `target` black pixels but from different row
//           patterns:
//           Rule 3 fails; row-pattern count prevents counting it.
// 
//         * Identical rows appear more than `target` times:
//           They cannot form valid pixels for their black columns, because any
//           such column would have at least more than `target` black pixels from
//           those rows alone.
// 
//         * target = 1:
//           The logic still works; a valid row pattern must appear once and a
//           valid column must have one black pixel.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples.
//         * All white except one black pixel.
//         * Identical target rows with valid columns.
//         * Columns with correct count but mixed row patterns.
//         * Random small grids compared with a brute-force rule checker.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal up to constant factors: we must inspect the
//         grid, so O(mn) time is necessary.  The row-pattern Counter is the clean
//         way to avoid repeated row comparisons.
//         """
// 
//         rows = len(picture)
//         cols = len(picture[0])
// 
//         column_black_count = [0] * cols
//         row_count: Counter[str] = Counter()
// 
//         for row in picture:
//             row_pattern = "".join(row)
//             row_count[row_pattern] += 1
// 
//             for col, value in enumerate(row):
//                 if value == "B":
//                     column_black_count[col] += 1
// 
//         answer = 0
//         for row_pattern, occurrences in row_count.items():
//             if occurrences != target:
//                 continue
// 
//             if row_pattern.count("B") != target:
//                 continue
// 
//             for col, value in enumerate(row_pattern):
//                 if value == "B" and column_black_count[col] == target:
//                     answer += target
// 
//         return answer
// # lc-original code=end

// @lc code=start
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
public:
    int findBlackPixel(vector<vector<char>>& picture, int target) {
        int rows = picture.size(), cols = picture[0].size();
        vector<int> colCount(cols);
        unordered_map<string, int> rowCount;
        for (auto& row : picture) {
            string pat(row.begin(), row.end());
            ++rowCount[pat];
            for (int c = 0; c < cols; ++c) if (row[c] == 'B') ++colCount[c];
        }
        int ans = 0;
        for (auto& [pat, occ] : rowCount) {
            if (occ != target) continue;
            if (count(pat.begin(), pat.end(), 'B') != target) continue;
            for (int c = 0; c < cols; ++c) if (pat[c] == 'B' && colCount[c] == target) ans += target;
        }
        return ans;
    }
};
// @lc code=end
