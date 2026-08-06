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
    ListNode* insertionSortList(ListNode* head) {
        /*
        Approach: build a sorted list behind a dummy head. For each original
        node, find the insertion point in the sorted prefix and splice the node
        there.

        Complexity: O(n^2) time in the worst case, O(1) extra space.
        */
        ListNode dummy(0);
        ListNode* cur = head;
        while (cur) {
            ListNode* next = cur->next;
            ListNode* prev = &dummy;
            while (prev->next && prev->next->val < cur->val) prev = prev->next;
            cur->next = prev->next;
            prev->next = cur;
            cur = next;
        }
        return dummy.next;
    }
};
