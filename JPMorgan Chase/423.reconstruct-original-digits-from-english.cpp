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
    string originalDigits(string s) {
        vector<int> cnt(26), digit(10);
        for (char c : s) ++cnt[c - 'a'];
        digit[0] = cnt['z' - 'a'];
        digit[2] = cnt['w' - 'a'];
        digit[4] = cnt['u' - 'a'];
        digit[6] = cnt['x' - 'a'];
        digit[8] = cnt['g' - 'a'];
        digit[3] = cnt['h' - 'a'] - digit[8];
        digit[5] = cnt['f' - 'a'] - digit[4];
        digit[7] = cnt['s' - 'a'] - digit[6];
        digit[1] = cnt['o' - 'a'] - digit[0] - digit[2] - digit[4];
        digit[9] = cnt['i' - 'a'] - digit[5] - digit[6] - digit[8];
        string ans;
        for (int d = 0; d <= 9; ++d) ans.append(digit[d], char('0' + d));
        return ans;
    }
};

/*
Interview explanation:
Unique letters identify several digits first: z, w, u, x, g correspond to 0,2,4,6,8. After those counts are known, remaining digits are determined by letters whose ambiguity has been removed.

C++ data structures: vector<int> of size 26 is faster and simpler than unordered_map for fixed lowercase letters.

Edge cases: repeated digits are emitted by string::append(count, char), and the loop emits them sorted.

Complexity: O(n) time and O(1) space.
*/
