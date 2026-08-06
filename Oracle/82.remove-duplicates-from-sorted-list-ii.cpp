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
    ListNode* deleteDuplicates(ListNode* head) {
        /*
        Approach:
        Sorted duplicates appear in runs. A dummy node handles removal at the
        head. prev points to the last confirmed unique node; cur scans each run
        and skips it completely if a duplicate was seen.

        Complexity: O(n) time and O(1) space.
        */
        ListNode dummy(0, head);
        ListNode* prev = &dummy;
        ListNode* cur = head;
        while (cur) {
            bool duplicate = false;
            while (cur->next && cur->val == cur->next->val) {
                duplicate = true;
                cur = cur->next;
            }
            if (duplicate) prev->next = cur->next;
            else prev = prev->next;
            cur = cur->next;
        }
        return dummy.next;
    }
};
