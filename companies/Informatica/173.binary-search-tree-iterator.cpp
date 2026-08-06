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


class BSTIterator {
    vector<TreeNode*> st;

    void pushLeft(TreeNode* node) {
        while (node) {
            st.push_back(node);
            node = node->left;
        }
    }

public:
    BSTIterator(TreeNode* root) {
        /*
        Approach: iterative inorder traversal. The stack stores the path to the
        next smallest node. next() pops one node and pushes the left spine of its
        right subtree.

        C++ notes: vector<TreeNode*> is used as a stack of raw tree pointers.
        Complexity: next and hasNext are O(1) amortized time, O(h) space.
        */
        pushLeft(root);
    }

    int next() {
        TreeNode* node = st.back();
        st.pop_back();
        pushLeft(node->right);
        return node->val;
    }

    bool hasNext() { return !st.empty(); }
};
