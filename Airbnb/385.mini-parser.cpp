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

class NestedInteger {
    bool integer;
    int value;
    vector<NestedInteger> values;

public:
    NestedInteger() : integer(false), value(0) {}
    NestedInteger(int value) : integer(true), value(value) {}
    bool isInteger() const { return integer; }
    int getInteger() const { return value; }
    const vector<NestedInteger>& getList() const { return values; }
    void add(const NestedInteger& ni) {
        if (integer) {
            integer = false;
            values.clear();
        }
        values.push_back(ni);
    }
    void setInteger(int newValue) {
        integer = true;
        value = newValue;
        values.clear();
    }
};

class Solution {
public:
    NestedInteger deserialize(string s) {
        if (s[0] != '[') return NestedInteger(stoi(s));
        vector<NestedInteger> st;
        int numberStart = -1;
        for (int i = 0; i < (int)s.size(); ++i) {
            char c = s[i];
            if (c == '[') {
                st.push_back(NestedInteger());
            } else if (c == ']' || c == ',') {
                if (numberStart != -1) {
                    st.back().add(NestedInteger(stoi(s.substr(numberStart, i - numberStart))));
                    numberStart = -1;
                }
                if (c == ']') {
                    NestedInteger finished = st.back();
                    st.pop_back();
                    if (st.empty()) return finished;
                    st.back().add(finished);
                }
            } else if (numberStart == -1) {
                numberStart = i;
            }
        }
        return NestedInteger();
    }
};

/*
Interview explanation:
Use a stack of NestedInteger lists matching open brackets. Numbers are parsed by remembering their start index and converting when a comma or closing bracket ends them.

C++ data structures: vector<NestedInteger> is used as a stack. The file includes a small NestedInteger implementation so the translation is standalone; LeetCode provides an equivalent interface in its judge.

Edge cases: a plain integer has no bracket and returns immediately; negative and multi-digit integers are handled by stoi on the substring.

Complexity: O(n) time and O(depth) stack space, excluding the output nested structure.
*/
