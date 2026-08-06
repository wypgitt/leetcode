#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// Definition for a binary tree node.
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
    int sumNumbers(TreeNode* root) {
        /*
        Approach: DFS carries the number represented by the current root-to-node
        path. Moving to a child appends one digit with current * 10 + node->val.
        At a leaf, that accumulated number contributes to the total.

        C++ notes: TreeNode* is the LeetCode binary-tree pointer type; nullptr
        marks an empty child.
        Complexity: O(n) time, O(h) recursion space.
        */
        function<int(TreeNode*, int)> dfs = [&](TreeNode* node, int current) -> int {
            if (!node) return 0;
            current = current * 10 + node->val;
            if (!node->left && !node->right) return current;
            return dfs(node->left, current) + dfs(node->right, current);
        };
        return dfs(root, 0);
    }
};
