/*
 * @lc app=leetcode id=272 lang=cpp
 *
 * [272] Closest Binary Search Tree Value II
 */
// Translated from 272.closest-binary-search-tree-value-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=272 lang=python3
// #
// # [272] Closest Binary Search Tree Value II
// #
// # =============================================================================
// # PROBLEM (precise)
// # =============================================================================
// #
// # Given the root of a binary search tree, a **target** (often float), and integer
// # **k**, return **exactly k** node values whose numeric distance to **target** is
// # smallest among all nodes. If multiple nodes tie for distance, usually prefer the
// # **smaller** value first (LeetCode convention — reflected in tie-breaking below).
// #
// # =============================================================================
// # WHY THIS APPROACH (algorithm choice)
// # =============================================================================
// #
// # **BST invariant:** an **inorder traversal** visits keys in **strictly sorted**
// # order (assuming distinct BST keys as is typical on LC).
// #
// # Once values are sorted in array **vals**, finding **k** closest to **target** is a
// # **two-pointer expansion** around the interval where **target** would be inserted:
// # - Locate split index **i = bisect_left(vals, target)** so values `< target` are to
// #   the left and values `>= target` to the right (adjust semantics if duplicates).
// # - Initialize **left = i - 1**, **right = i**, then repeatedly pick the side whose
// #   endpoint is **strictly closer** to **target**; on **equal** distance, pick the
// #   **smaller** number (move **left** first) — matches typical tie rule.
// #
// # **Alternatives (trade-offs to mention in interviews):**
// #
// # - **Max-heap of size k** storing (-distance, value) while traversing: **O(n log k)**
// #   time, **O(k)** space — never stores full sorted list; good if **k ≪ n** and tree
// #   is huge (still must visit every node unless combined with pruning — BST alone
// #   doesn’t reduce worst-case visit without extra structure).
// #
// # - **Two-stack predecessor/successor iterators:** simulate **prev** and **next** on a
// #   BST without materializing all nodes — **O(h + k)** extra space, **O(n)** time in
// #   worst case to advance pointers enough — elegant but longer to code under time
// #   pressure.
// #
// # Here we choose **inorder + two pointers**: **simple**, easy to prove correct, **O(n)**
// # time / **O(n)** auxiliary for the sorted snapshot — standard “hire loop” solution.
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # - **vals:** Python **list** holding inorder sequence — **O(n)** space.
// # - **Iterative inorder stack:** explicit **list as stack** for traversal — avoids deep
// #   recursion on skewed trees; still **O(h)** stack frames worst-case height **h**.
// # - **bisect_left** from **bisect** module on sorted **vals** — **O(log n)** locate split.
// #
// # No hash map needed — ordering comes from BST structure.
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY (analysis)
// # =============================================================================
// #
// # **Time:**
// # - Inorder visits each node once → **O(n)**.
// # - Bisect on length **n** → **O(log n)**.
// # - Each pointer moves at most **n** steps total while collecting **k** answers → **O(k)**.
// # - Overall **O(n)** dominated by traversal.
// #
// # **Space:**
// # - **vals** stores **n** integers → **O(n)** auxiliary (plus **O(h)** stack during inorder,
// #   absorbed into **O(n)** worst case on skewed tree where **h = n**).
// #
// # **Improvement axis:** reduce extra space using iterator-based successor/predecessor
// # (**O(h)** memory) at the cost of implementation complexity.
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # - **Empty tree:** return **[]**.
// # - **k ≥ n:** collect entire inorder list; merge still completes in **k** steps when
// #   **k == n** (both pointers exhaust predictably).
// # - **k == 1:** degenerates to closest single value — same code path.
// # - **Target smaller than min / larger than max:** one-sided expansion only.
// # - **Duplicate values in BST:** LC sometimes forbids dupes in BST definition; if dupes
// #   exist, ordering/tie rules may need clarification — standard BST assumption here.
// #
// # =============================================================================
// # TESTING
// # =============================================================================
// #
// # - Small handcrafted trees + brute force (collect all values, sort by distance then
// #   value tie-break, take **k**).
// # - Random BST shapes via insertion order vs brute.
// #
// # =============================================================================
// 
// # lc-original code=start
// import bisect
// from typing import List, Optional
// 
// 
// # Definition for a binary tree node.
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// class Solution:
//     def closestKValues(self, root: Optional[TreeNode], target: float, k: int) -> List[int]:
//         """
//         Inorder flatten BST to sorted values, locate split around target, expand two
//         pointers picking the closer endpoint each step (smaller on ties).
//         """
//         if not root or k <= 0:
//             return []
// 
//         vals: List[int] = []
//         stack = []
//         cur = root
//         while stack or cur:
//             while cur:
//                 stack.append(cur)
//                 cur = cur.left
//             cur = stack.pop()
//             vals.append(cur.val)
//             cur = cur.right
// 
//         n = len(vals)
//         i = bisect.bisect_left(vals, target)
//         left, right = i - 1, i
//         out: List[int] = []
//         need = min(k, n)
//         while len(out) < need:
//             if left < 0:
//                 out.append(vals[right])
//                 right += 1
//             elif right >= n:
//                 out.append(vals[left])
//                 left -= 1
//             elif abs(vals[left] - target) <= abs(vals[right] - target):
//                 out.append(vals[left])
//                 left -= 1
//             else:
//                 out.append(vals[right])
//                 right += 1
//         return out
// 
// 
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
    vector<int> closestKValues(TreeNode* root, double target, int k) {
        if (!root || k <= 0) return {};
        vector<int> vals;
        vector<TreeNode*> st;
        TreeNode* cur = root;
        while (!st.empty() || cur) {
            while (cur) {
                st.push_back(cur);
                cur = cur->left;
            }
            cur = st.back();
            st.pop_back();
            vals.push_back(cur->val);
            cur = cur->right;
        }
        int n = vals.size();
        int right = lower_bound(vals.begin(), vals.end(), target) - vals.begin();
        int left = right - 1;
        vector<int> out;
        while ((int)out.size() < min(k, n)) {
            if (left < 0) out.push_back(vals[right++]);
            else if (right >= n) out.push_back(vals[left--]);
            else if (abs(vals[left] - target) <= abs(vals[right] - target)) out.push_back(vals[left--]);
            else out.push_back(vals[right++]);
        }
        return out;
    }
};
// @lc code=end
