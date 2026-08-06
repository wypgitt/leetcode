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
    void reorderList(ListNode* head) {
        /*
        Approach: split the list in half, reverse the second half, then weave
        nodes from first and reversed second halves: L0, Ln, L1, Ln-1, ... .

        C++ notes: all work is done by rewiring ListNode* next pointers; no new
        list nodes are allocated.
        Complexity: O(n) time, O(1) space.
        */
        if (!head || !head->next) return;
        ListNode* slow = head;
        ListNode* fast = head->next;
        while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }
        ListNode* second = slow->next;
        slow->next = nullptr;
        ListNode* prev = nullptr;
        while (second) {
            ListNode* next = second->next;
            second->next = prev;
            prev = second;
            second = next;
        }
        ListNode* first = head;
        second = prev;
        while (second) {
            ListNode* fnext = first->next;
            ListNode* snext = second->next;
            first->next = second;
            second->next = fnext;
            first = fnext;
            second = snext;
        }
    }
};
