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


class MinStack {
    vector<pair<int,int>> st;

public:
    MinStack() {
        /*
        Approach: store each pushed value together with the minimum value at or
        below that stack position. top() reads first, getMin() reads second.

        C++ notes: vector<pair<int,int>> is a compact stack of (value,currentMin)
        pairs using push_back/pop_back.
        Complexity: all operations O(1), O(n) space.
        */
    }

    void push(int val) {
        int currentMin = st.empty() ? val : min(val, st.back().second);
        st.push_back({val, currentMin});
    }

    void pop() { st.pop_back(); }

    int top() { return st.back().first; }

    int getMin() { return st.back().second; }
};
