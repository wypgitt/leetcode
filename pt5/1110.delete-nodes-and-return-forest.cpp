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
// struct TreeNode {
//     int val;
//     TreeNode *left;
//     TreeNode *right;
//     TreeNode() : val(0), left(nullptr), right(nullptr) {}
//     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
//     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
// };

class Solution {
public:
    vector<TreeNode*> delNodes(TreeNode* root, vector<int>& to_delete) {
        unordered_set<int> deleted(to_delete.begin(), to_delete.end());
        vector<TreeNode*> forest;
        dfs(root, true, deleted, forest);
        return forest;
    }

private:
    TreeNode* dfs(TreeNode* node, bool isRoot, const unordered_set<int>& deleted, vector<TreeNode*>& forest) {
        if (!node) return nullptr;

        bool remove = deleted.count(node->val) > 0;
        if (isRoot && !remove) forest.push_back(node);

        node->left = dfs(node->left, remove, deleted, forest);
        node->right = dfs(node->right, remove, deleted, forest);

        return remove ? nullptr : node;
    }
};

/*
Interview Explanation

Core idea:
Deleting a node makes each non-deleted child the root of a new tree. DFS can
decide whether the current node is deleted and pass that fact to its children.

C++ data structures:
- unordered_set<int> gives O(1) average membership checks for deleted values.
- vector<TreeNode*> stores roots of the resulting forest.
- The tree is rewired in place by assigning node->left and node->right to DFS
  results.

Algorithm:
1. DFS with a boolean isRoot meaning the current node has no surviving parent.
2. If current node is a root and not deleted, add it to forest.
3. Recurse into children; if current node is deleted, children become roots.
4. Return nullptr for deleted nodes, otherwise return the node.

Correctness:
Every surviving component root is either the original root with no deleted
parent, or a child of a deleted node. The DFS adds exactly those nodes when they
are not deleted. Returning nullptr removes deleted nodes from their parents,
so the final pointers define exactly the requested forest.

Complexity:
O(n) time and O(n) space for recursion in the worst case plus the deletion set.

Edge cases:
- Deleting the original root promotes surviving children.
- Deleting a leaf simply disconnects it.
- If no nodes are deleted, forest contains only root.
*/
