#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    int connectSticks(vector<int>& sticks) {
        priority_queue<int, vector<int>, greater<int>> pq(sticks.begin(), sticks.end());
        int cost = 0;

        while (pq.size() > 1) {
            int a = pq.top(); pq.pop();
            int b = pq.top(); pq.pop();
            cost += a + b;
            pq.push(a + b);
        }

        return cost;
    }
};

/*
Interview Explanation

Core idea:
This is the optimal merge pattern. Always combine the two shortest sticks first
to minimize how often large lengths are paid again later.

C++ data structures:
- priority_queue with greater<int> is a min-heap.

Algorithm:
1. Push all stick lengths into the min-heap.
2. Pop two smallest, add their sum to cost, and push the combined stick.
3. Repeat until one stick remains.

Correctness:
The two smallest sticks can be merged first in some optimal solution by the
same exchange argument used for Huffman coding. Merging them creates a smaller
subproblem with their combined length. Repeating greedily is optimal.

Complexity:
O(n log n) time and O(n) space.

Edge cases:
- Zero or one stick costs 0.
- Equal lengths are handled naturally by the heap.
*/
