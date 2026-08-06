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
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
        /*
        Approach: use the BST ordering. If both targets are smaller than node,
        move left. If both are larger, move right. The first node between the two
        values is the split point and therefore the LCA.

        Complexity: O(h) time, O(1) space.
        */
        int low = min(p->val, q->val), high = max(p->val, q->val);
        TreeNode* node = root;
        while (node) {
            if (high < node->val) node = node->left;
            else if (low > node->val) node = node->right;
            else return node;
        }
        return nullptr;
    }
};
