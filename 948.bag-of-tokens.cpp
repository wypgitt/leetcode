// Translated from 948.bag-of-tokens.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=948 lang=python3
// #
// # [948] Bag Of Tokens
// #
// 
// # --- Interview notes (greedy two pointers, exchange argument, complexity) ---
// #
// # Problem
// # **`tokens`** are integer costs. Start with **`power`** points and **score** **`0`**. Each unused token can be played:
// # • **Face up** — pay **`tokens[i]`** power; **score += 1`** (only if you can afford it).
// # • **Face down** — requires **score ≥ 1** before playing; **gain `tokens[j]`** power and **score -= 1`**.
// # Maximize **final** achievable score (actually maximum score **at any time** — problem asks maximum score you can obtain; playing face-down
// # lowers score temporarily but may enable more face-ups later — we track **peak** score).
// #
// # Greedy strategy (sorted array + two pointers)
// # Sort **`tokens`** ascending. Maintain **`lo`** (cheapest remaining) and **`hi`** (most expensive remaining).
// # • **If `power ≥ tokens[lo]`** — buy the **cheapest** face-up: cheapest gives **maximum tokens per unit power** among remaining buys, so
// #   greedy **locally optimal** for increasing score.
// # • **Else**, if **`score > 0`** — sell the **most expensive** face-down: losing one score point while reclaiming **as much power as
// #   possible** is the best trade if we must “borrow” power to continue.
// # • **Else** — stuck (no power to buy, cannot sell), **stop**.
// # Track **`answer = max(answer, score)`** after each successful face-up (only face-ups increase score).
// #
// # Why selling the largest token is optimal when forced
// # Any face-down loses **exactly 1** score; choosing **`tokens[hi]`** maximizes power gained, enlarging the chance to afford more cheap
// # face-ups afterward — standard exchange argument vs selling a cheaper remaining token.
// #
// # Why buying the smallest token first when affordable
// # Spending power on the **minimum** cost buys **one** score while preserving **maximum residual power** for future moves compared to
// # spending on a larger token first.
// #
// # Data structures
// # **`list`** sorted in place (**`O(n log n)`**); **`lo`**, **`hi`** indices — **`O(1)`** extra.
// #
// # Time complexity **`O(n log n)`** from sorting; scan **`O(n)`**.
// #
// # Space complexity **`O(1)`** auxiliary if sorting in place (**`O(log n)`** sort stack depending on implementation).
// #
// # Edge cases
// # • **Empty **`tokens`** → **`0`**.
// # • **Never affordable** — **`power < min(tokens)`** and score stays **`0`** → **`0`**.
// # • **Power buys everything** — monotone face-ups only.
// #
// # Tests (LeetCode)
// # • **`tokens = [100], power = 50`** → **`0`** (cannot play face-up).
// # • **`tokens = [100,200], power = 150`** → **`1`** (buy **`100`**, optional trade later).
// # • **`tokens = [100,200,300,400], power = 200`** → **`2`**.
// #
// # Improvements
// # • **Counting sort** if costs bounded small — linear time possible; default **`int`** costs use comparison sort.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def bagOfTokensScore(self, tokens: List[int], power: int) -> int:
//         tokens.sort()
//         lo, hi = 0, len(tokens) - 1
//         score = 0
//         best = 0
// 
//         while lo <= hi:
//             if power >= tokens[lo]:
//                 power -= tokens[lo]
//                 lo += 1
//                 score += 1
//                 if score > best:
//                     best = score
//             elif score > 0:
//                 power += tokens[hi]
//                 hi -= 1
//                 score -= 1
//             else:
//                 break
// 
//         return best
// 
// 
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
public:
    int bagOfTokensScore(vector<int>& tokens, int power) {
        sort(tokens.begin(), tokens.end());
        int lo = 0, hi = tokens.size() - 1, score = 0, best = 0;
        while (lo <= hi) {
            if (power >= tokens[lo]) {
                power -= tokens[lo++];
                best = max(best, ++score);
            } else if (score > 0) {
                power += tokens[hi--];
                --score;
            } else break;
        }
        return best;
    }
};
