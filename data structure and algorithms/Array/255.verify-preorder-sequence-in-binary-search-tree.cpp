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
    bool verifyPreorder(vector<int>& preorder) {
        /*
        Approach: simulate DFS preorder bounds with a stack. lower is the minimum
        allowed value after moving into a right subtree. While the current value
        is greater than the stack top, pop ancestors and update lower. Any later
        value below lower violates the BST preorder property.

        Complexity: O(n) time, O(n) stack space.
        */
        vector<int> st;
        long long lower = LLONG_MIN;
        for (int value : preorder) {
            if (value < lower) return false;
            while (!st.empty() && value > st.back()) {
                lower = st.back();
                st.pop_back();
            }
            st.push_back(value);
        }
        return true;
    }
};
