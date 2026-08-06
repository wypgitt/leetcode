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

// Definition for singly-linked list.
// struct ListNode {
//     int val;
//     ListNode *next;
//     ListNode() : val(0), next(nullptr) {}
//     ListNode(int x) : val(x), next(nullptr) {}
//     ListNode(int x, ListNode *next) : val(x), next(next) {}
// };

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
    TreeNode* sortedListToBST(ListNode* head) {
        /*
        Approach:
        Count the list, then simulate inorder construction. Build the left half,
        consume the current list node as root, then build the right half. This
        uses sorted list order once and produces a height-balanced BST.

        C++ notes:
        A captured ListNode* current advances as recursive calls consume nodes.

        Complexity: O(n) time and O(log n) recursion space for the balanced tree.
        */
        int length = 0;
        for (ListNode* cur = head; cur; cur = cur->next) ++length;
        ListNode* current = head;
        function<TreeNode*(int)> build = [&](int size) -> TreeNode* {
            if (size <= 0) return nullptr;
            TreeNode* left = build(size / 2);
            TreeNode* root = new TreeNode(current->val);
            current = current->next;
            root->left = left;
            root->right = build(size - size / 2 - 1);
            return root;
        };
        return build(length);
    }
};
