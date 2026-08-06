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
    string shiftingLetters(string s, vector<int>& shifts) {
        long long total = 0;
        for (int i = s.size() - 1; i >= 0; --i) {
            total = (total + shifts[i]) % 26;
            s[i] = char((s[i] - 'a' + total) % 26 + 'a');
        }
        return s;
    }
};

/*
Interview explanation:
Character i is shifted by the suffix sum shifts[i]+...+shifts[n-1]. Scan from right to left, maintaining that sum modulo 26.

C++ data structures: mutate the input string directly for output.

Edge cases: large shifts are reduced modulo 26; wraparound is handled by modular arithmetic.

Complexity: O(n) time and O(1) extra space besides the returned string.
*/
