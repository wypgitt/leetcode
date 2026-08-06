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
    int kthSmallest(TreeNode* root, int k) {
        /*
        Approach: inorder traversal of a BST visits values in ascending order.
        Use an explicit stack to visit nodes iteratively and stop when the kth
        node is popped.

        Complexity: O(h + k) time, O(h) space.
        */
        vector<TreeNode*> st;
        TreeNode* node = root;
        while (true) {
            while (node) { st.push_back(node); node = node->left; }
            node = st.back(); st.pop_back();
            if (--k == 0) return node->val;
            node = node->right;
        }
    }
};
