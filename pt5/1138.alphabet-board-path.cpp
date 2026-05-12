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
    string alphabetBoardPath(string target) {
        int row = 0, col = 0;
        string answer;

        for (char ch : target) {
            int index = ch - 'a';
            int nextRow = index / 5;
            int nextCol = index % 5;

            while (row > nextRow) { answer.push_back('U'); --row; }
            while (col > nextCol) { answer.push_back('L'); --col; }
            while (row < nextRow) { answer.push_back('D'); ++row; }
            while (col < nextCol) { answer.push_back('R'); ++col; }
            answer.push_back('!');
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
The only tricky cell is 'z' at row 5, col 0. Moving up before right and left
before down avoids stepping into invalid cells around 'z'.

C++ data structures:
- string answer is built incrementally.
- Row/column integers track the current board position.

Algorithm:
For each target character, compute its board coordinates. Move in this safe
order: U, L, D, R. Then append '!'.

Correctness:
For normal rows, all intermediate cells are valid. For moves to 'z', moving
left before down ensures we enter row 5 only at col 0. For moves away from
'z', moving up first leaves row 5 before any horizontal movement. Therefore
every emitted path is valid and reaches each target character.

Complexity:
O(total path length), which is O(26 * target length) in the worst case. Extra
space is the output string.

Edge cases:
- Consecutive same letters emit only '!'.
- Moving to and from 'z' stays valid.
*/
