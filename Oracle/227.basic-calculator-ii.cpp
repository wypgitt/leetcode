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
    int calculate(string s) {
        /*
        Approach: one pass with a stack of signed terms. '+' and '-' push terms;
        '*' and '/' immediately combine with the previous term to enforce higher
        precedence. A sentinel '+' flushes the final number.

        C++ notes: integer division truncates toward zero, matching the problem.
        Complexity: O(n) time, O(n) space.
        */
        vector<int> st;
        long long num = 0;
        char op = '+';
        s.push_back('+');
        for (char ch : s) {
            if (ch == ' ') continue;
            if (isdigit(static_cast<unsigned char>(ch))) {
                num = num * 10 + (ch - '0');
                continue;
            }
            if (op == '+') st.push_back((int)num);
            else if (op == '-') st.push_back((int)-num);
            else if (op == '*') st.back() *= (int)num;
            else st.back() /= (int)num;
            op = ch;
            num = 0;
        }
        return accumulate(st.begin(), st.end(), 0);
    }
};
