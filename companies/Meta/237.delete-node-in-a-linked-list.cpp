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

// Definition for singly-linked list.
// struct ListNode {
//     int val;
//     ListNode *next;
//     ListNode() : val(0), next(nullptr) {}
//     ListNode(int x) : val(x), next(nullptr) {}
//     ListNode(int x, ListNode *next) : val(x), next(next) {}
// };


class Solution {
public:
    void deleteNode(ListNode* node) {
        /*
        Approach: the node to delete is guaranteed not to be the tail, and only
        that node pointer is provided. Copy the next node's value into this node,
        then bypass the next node.

        Complexity: O(1) time, O(1) space.
        */
        node->val = node->next->val;
        node->next = node->next->next;
    }
};
