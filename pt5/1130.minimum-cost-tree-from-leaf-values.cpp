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
    int mctFromLeafValues(vector<int>& arr) {
        int cost = 0;
        vector<int> st = {INT_MAX};

        for (int value : arr) {
            while (st.back() <= value) {
                int mid = st.back();
                st.pop_back();
                cost += mid * min(st.back(), value);
            }
            st.push_back(value);
        }

        while (st.size() > 2) {
            int mid = st.back();
            st.pop_back();
            cost += mid * st.back();
        }

        return cost;
    }
};

/*
Interview Explanation

Core idea:
Each leaf except the global maximum is eventually multiplied by the smaller of
its nearest greater leaf on the left or right. A monotonic decreasing stack
finds those neighbors greedily.

C++ data structures:
- vector<int> acts as a stack.
- INT_MAX sentinel avoids empty-stack checks.

Algorithm:
1. Maintain a decreasing stack of leaf values.
2. When current value is >= stack top, pop the smaller leaf mid.
3. Pair mid with the smaller of its left greater neighbor and current value.
4. After scanning, collapse remaining stack from the end.

Correctness:
A smaller leaf should be combined with the smallest greater neighbor available;
combining it with a larger value would only increase cost. The first time a
value is popped, both nearest greater candidates are known, so the greedy
product is optimal.

Complexity:
Each value is pushed and popped once: O(n) time and O(n) space.

Edge cases:
- Two leaves produce their product.
- Strictly increasing or decreasing arrays are handled by stack collapsing.
*/
