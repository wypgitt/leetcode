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


class Solution {
public:
    ListNode* partition(ListNode* head, int x) {
        /*
        Approach:
        Build two lists with existing nodes: values less than x and values at
        least x. Appending preserves relative order within each partition. Then
        join the small list to the large list.

        Complexity: O(n) time and O(1) extra space.
        */
        ListNode beforeDummy(0), afterDummy(0);
        ListNode* before = &beforeDummy;
        ListNode* after = &afterDummy;
        while (head) {
            ListNode* next = head->next;
            head->next = nullptr;
            if (head->val < x) {
                before->next = head;
                before = before->next;
            } else {
                after->next = head;
                after = after->next;
            }
            head = next;
        }
        before->next = afterDummy.next;
        return beforeDummy.next;
    }
};
