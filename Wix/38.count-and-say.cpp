#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    string countAndSay(int n) {
        /*
        Approach:
        Start from "1". Each next term is formed by scanning runs of equal
        characters in the previous term and appending count followed by digit.

        Complexity: O(total generated characters) time and O(length of term)
        space.
        */
        string cur = "1";
        for (int step = 1; step < n; ++step) {
            string next;
            for (int i = 0; i < (int)cur.size();) {
                int j = i;
                while (j < (int)cur.size() && cur[j] == cur[i]) ++j;
                next += to_string(j - i);
                next.push_back(cur[i]);
                i = j;
            }
            cur = move(next);
        }
        return cur;
    }
};
