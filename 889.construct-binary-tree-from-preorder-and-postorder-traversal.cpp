// Translated from 889.construct-binary-tree-from-preorder-and-postorder-traversal.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=889 lang=python3
// #
// # [889] Construct Binary Tree from Preorder and Postorder Traversal
// #
// 
// # =============================================================================
// # INTERVIEW: ELEVATOR PITCH (~30 seconds)
// # =============================================================================
// #
// # "Preorder is root, then left preorder, then right; postorder is left post, right
// # post, root — so the root is preorder[0] and postorder[-1]. The next preorder value
// # is the **left-subtree root** (we follow the convention that a lone child is treated
// # as the left child when ambiguous). That node’s position in postorder tells us how
// # many nodes belong to the left subtree — split both arrays by that size and recurse.
// # A hash map value→index in postorder makes each split O(1) lookup → **O(n)** total."
// #
// # =============================================================================
// # PROBLEM (PRECISE)
// # =============================================================================
// #
// # Unique integers `preorder` and `postorder` are traversals of the **same** binary
// # tree (not necessarily BST). Reconstruct **any** valid tree consistent with both.
// #
// # =============================================================================
// # TRAVERSAL STRUCTURE (FIX NOTATION)
// # =============================================================================
// #
// # • **Preorder:**  `[ root ] + preorder(left) + preorder(right)`
// # • **Postorder:** `postorder(left) + postorder(right) + [ root ]`
// #
// # Therefore the root value appears as **`preorder[0]`** and **`postorder[-1]`** (equal).
// #
// # =============================================================================
// # SPLITTING LEFT VS RIGHT — WHY `preorder[1]` AND POSTORDER INDEX
// # =============================================================================
// #
// # Assume **left subtree is non-empty** whenever the tree has more than one node (this
// # matches the standard solution on LeetCode and resolves **child ambiguity**: when the
// # tree has a **single child**, preorder/postorder cannot tell left vs right — both
// # interpretations yield the **same two traversals**, so building that child as **left**
// # is acceptable.)
// #
// # Then **`preorder[1]`** is the root of the **left** subtree. In **postorder**, the
// # left subtree occupies one contiguous prefix **before** the right subtree and root.
// # Within the left subtree’s **postorder**, the **last** element is the root of the left
// # subtree — so it equals **`preorder[1]`**.
// #
// # If **`preorder[1]`** appears at postorder index **`p`** (within the current segment
// # rooted at `post_lo`), then the left subtree has **`L = p - post_lo + 1`** nodes.
// #
// # Slice mentally:
// # • Left **preorder:**  indices `pre_lo+1 … pre_lo+L`
// # • Left **postorder:** indices `post_lo … post_lo+L-1`
// # • Right **preorder:** `pre_lo+L+1 … pre_hi`
// # • Right **postorder:** `post_lo+L … pre_hi-1` but root at end → `post_lo+L … post_hi-1`
// #   (excluding global root already isolated by recursion bounds)
// #
// # Recurse on both children with **half-open index ranges** (implemented below with
// # inclusive `[a,b]` and `[c,d]` for clarity).
// #
// # =============================================================================
// # WHY HASH MAP `value → postorder index`
// # =============================================================================
// #
// # To compute **`L`** we need the index of **`preorder[pre_lo+1]`** inside the **current**
// # postorder segment. Values are **unique**, so a global map **`value → index`** in the
// # **full** `postorder` array still gives the correct position for lookups (each value
// # appears exactly once). Then **`L = pos[lv] - post_lo + 1`** is the left subtree size.
// #
// # Alternative: **`list.index`** on slices — **O(length)** per call → **O(n²)** overall.
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY
// # =============================================================================
// #
// # • **Build map:** **O(n)** time, **O(n)** space.
// # • **Recursion:** each node built once → **O(n)** total time; recursion depth **O(h)**
// #   ≤ **O(n)** stack space worst case (skewed tree).
// # • **No auxiliary trees** besides output — aside from map + recursion stack,
// #   **O(n)** extra.
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # • **`n == 1`** — leaf; no recursive split.
// # • **Single-child ambiguity** — discussed above; attaching as **left** is standard.
// # • **Balanced vs skewed** — affects **recursion depth**, not asymptotic node work.
// #
// # =============================================================================
// # TESTING (SANITY)
// # =============================================================================
// #
// # • Compare **preorder/postorder** recomputed from built tree via traversals (must
// #   match input — up to ambiguous single-child shapes).
// # • Small trees brute-generated / known fixtures from LeetCode examples.
// #
// # =============================================================================
// # IMPROVEMENTS / VARIANTS
// # =============================================================================
// #
// # • **Iterative stack simulation** — possible but recursion mirrors traversal structure.
// # • **Slice-based recursion** — simpler code but **O(n²)** copying in Python; index ranges
// #   + map preferred for interviews when performance matters.
// #
// # =============================================================================
// #
// # LeetCode note: Do **not** define your own `TreeNode` class in the submission — the
// # judge injects `TreeNode`. A duplicate class makes `TreeNode(...)` build **your**
// # type while the grader expects **its** type → `TypeError` / serialization failure.
// # For local testing only, uncomment the stub below or define `TreeNode` in another cell.
// #
// # =============================================================================
// 
// # @lc code=start
// from typing import Dict, List, Optional
// 
// 
// # Definition for a binary tree node (provided by LeetCode — do not redefine when submitting).
// # class TreeNode:
// #     def __init__(self, val=0, left=None, right=None):
// #         self.val = val
// #         self.left = left
// #         self.right = right
// 
// 
// class Solution:
//     def constructFromPrePost(
//         self, preorder: List[int], postorder: List[int]
//     ) -> Optional["TreeNode"]:
//         """
//         Build any binary tree consistent with preorder and postorder (unique values).
// 
//         Map each value to its postorder index for O(1) left-subtree size (L).
//         Recurse on index ranges without slicing arrays.
//         """
//         pos: Dict[int, int] = {v: i for i, v in enumerate(postorder)}
// 
//         def build(pre_lo: int, pre_hi: int, post_lo: int, post_hi: int) -> Optional["TreeNode"]:
//             if pre_lo > pre_hi:
//                 return None
//             root_val = preorder[pre_lo]
//             node = TreeNode(root_val)
//             if pre_lo == pre_hi:
//                 return node
// 
//             left_root_val = preorder[pre_lo + 1]
//             # Size of left subtree (nodes); root of left is last in left's postorder.
//             L = pos[left_root_val] - post_lo + 1
// 
//             node.left = build(pre_lo + 1, pre_lo + L, post_lo, post_lo + L - 1)
//             node.right = build(pre_lo + L + 1, pre_hi, post_lo + L, post_hi - 1)
//             return node
// 
//         n = len(preorder)
//         return build(0, n - 1, 0, n - 1)
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
    TreeNode* constructFromPrePost(vector<int>& preorder, vector<int>& postorder) {
        unordered_map<int, int> pos;
        for (int i = 0; i < (int)postorder.size(); ++i) pos[postorder[i]] = i;
        function<TreeNode*(int, int, int, int)> build = [&](int preLo, int preHi, int postLo, int postHi) -> TreeNode* {
            if (preLo > preHi) return nullptr;
            TreeNode* node = new TreeNode(preorder[preLo]);
            if (preLo == preHi) return node;
            int leftRoot = preorder[preLo + 1];
            int L = pos[leftRoot] - postLo + 1;
            node->left = build(preLo + 1, preLo + L, postLo, postLo + L - 1);
            node->right = build(preLo + L + 1, preHi, postLo + L, postHi - 1);
            return node;
        };
        int n = preorder.size();
        return build(0, n - 1, 0, n - 1);
    }
};
