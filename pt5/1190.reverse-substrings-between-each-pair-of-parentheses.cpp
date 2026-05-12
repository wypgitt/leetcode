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
    string reverseParentheses(string s) {
        int n = s.size();
        vector<int> match(n);
        stack<int> st;

        for (int i = 0; i < n; ++i) {
            if (s[i] == '(') {
                st.push(i);
            } else if (s[i] == ')') {
                int j = st.top();
                st.pop();
                match[i] = j;
                match[j] = i;
            }
        }

        string answer;
        for (int i = 0, step = 1; i < n; i += step) {
            if (s[i] == '(' || s[i] == ')') {
                i = match[i];
                step = -step;
            } else {
                answer.push_back(s[i]);
            }
        }
        return answer;
    }
};

/*
Interview Explanation

Core idea:
Precompute matching parentheses. Then walk through the string; whenever a
parenthesis is hit, jump to its match and reverse direction.

C++ data structures:
- stack<int> matches parentheses.
- vector<int> match stores partner index for each parenthesis.
- string answer collects letters only.

Algorithm:
1. Use a stack to pair parentheses.
2. Traverse with index i and direction step.
3. On a parenthesis, jump to its match and flip step.
4. On a letter, append it.

Correctness:
Reversing inside parentheses is equivalent to traversing that interval in the
opposite direction. Nested parentheses cause repeated jumps and direction
flips, exactly simulating all reversals without modifying the string.

Complexity:
O(n) time and O(n) space.

Edge cases:
- Nested parentheses are handled by stack matches.
- Parentheses themselves are omitted from output.
*/
