#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
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
    void flatten(TreeNode* root) {
        /*
        Approach:
        The flattened order is preorder. Process nodes in reverse preorder
        (right, left, root) while prev points to the already-flattened suffix.
        Set node->right to prev, clear node->left, then move prev to node.

        Complexity: O(n) time and O(h) recursion space.
        */
        TreeNode* prev = nullptr;
        function<void(TreeNode*)> dfs = [&](TreeNode* node) {
            if (!node) return;
            dfs(node->right);
            dfs(node->left);
            node->right = prev;
            node->left = nullptr;
            prev = node;
        };
        dfs(root);
    }
};
