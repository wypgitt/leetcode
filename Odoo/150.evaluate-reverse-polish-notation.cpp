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
    int evalRPN(vector<string>& tokens) {
        /*
        Approach: scan tokens with a stack. Numbers are pushed. An operator pops
        b then a, evaluates a op b, and pushes the result. Division must truncate
        toward zero, which C++ integer division already does.

        C++ notes: vector<int> is used as a stack with push_back/pop_back.
        Complexity: O(n) time, O(n) space.
        */
        vector<int> st;
        for (const string& token : tokens) {
            if (token != "+" && token != "-" && token != "*" && token != "/") {
                st.push_back(stoi(token));
                continue;
            }
            int b = st.back(); st.pop_back();
            int a = st.back(); st.pop_back();
            if (token == "+") st.push_back(a + b);
            else if (token == "-") st.push_back(a - b);
            else if (token == "*") st.push_back(a * b);
            else st.push_back(a / b);
        }
        return st.back();
    }
};
