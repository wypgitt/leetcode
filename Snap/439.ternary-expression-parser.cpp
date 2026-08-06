#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    string parseTernary(string expression) {
        vector<char> st;
        for (int i = (int)expression.size() - 1; i >= 0; --i) {
            char c = expression[i];
            if (!st.empty() && st.back() == '?') {
                st.pop_back();
                char trueExpr = st.back(); st.pop_back();
                st.pop_back();
                char falseExpr = st.back(); st.pop_back();
                st.push_back(c == 'T' ? trueExpr : falseExpr);
            } else if (c != ':') {
                st.push_back(c);
            } else {
                st.push_back(c);
            }
        }
        return string(1, st.back());
    }
};

/*
Interview explanation:
Ternary expressions are right-associative. Scanning right to left means each branch expression is already resolved when its condition is encountered.

C++ data structures: vector<char> is used as a stack for compact push_back/pop_back operations.

Edge cases: nested ternaries collapse from right to left; leaves are single characters by constraint.

Complexity: O(n) time and O(n) space.
*/
