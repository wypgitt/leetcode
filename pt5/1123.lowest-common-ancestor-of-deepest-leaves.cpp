#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// LeetCode provides TreeNode.
// struct TreeNode { int val; TreeNode *left; TreeNode *right; };

class Solution {
public:
    TreeNode* lcaDeepestLeaves(TreeNode* root) {
        return dfs(root).second;
    }

private:
    pair<int, TreeNode*> dfs(TreeNode* node) {
        if (!node) return {0, nullptr};
        auto left = dfs(node->left);
        auto right = dfs(node->right);

        if (left.first > right.first) return {left.first + 1, left.second};
        if (right.first > left.first) return {right.first + 1, right.second};
        return {left.first + 1, node};
    }
};

/*
Interview Explanation

Core idea:
For each subtree, return both its maximum depth and the LCA of its deepest
leaves. If left and right depths tie, the current node is the LCA.

C++ data structures:
- pair<int, TreeNode*> carries {deepest depth, lca node}.

Algorithm:
1. DFS left and right.
2. If one side is deeper, propagate that side's LCA.
3. If depths are equal, current node is the LCA for deepest leaves in both
   sides.

Correctness:
The deepest leaves of a subtree are either all in the deeper child, or split
across both children when depths tie. The recurrence returns the correct LCA in
both cases, and applying it at the root gives the answer.

Complexity:
O(n) time and O(h) recursion space.

Edge cases:
- Single node returns itself.
- Deepest leaves all on one side propagate that side's result.
*/
