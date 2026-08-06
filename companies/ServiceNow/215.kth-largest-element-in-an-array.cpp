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


class Solution {
public:
    int findKthLargest(vector<int>& nums, int k) {
        /*
        Approach: keep a min-heap of the k largest values seen so far. Push each
        number, and if the heap grows beyond k, remove the smallest. The heap top
        is then the kth largest value.

        C++ notes: priority_queue with greater<int> is a min-heap.
        Complexity: O(n log k) time, O(k) space.
        */
        priority_queue<int, vector<int>, greater<int>> heap;
        for (int num : nums) {
            heap.push(num);
            if ((int)heap.size() > k) heap.pop();
        }
        return heap.top();
    }
};
