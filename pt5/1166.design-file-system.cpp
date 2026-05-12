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

class FileSystem {
private:
    unordered_map<string, int> values;

public:
    FileSystem() {
        values[""] = -1;
    }

    bool createPath(string path, int value) {
        if (values.count(path)) return false;
        int slash = path.find_last_of('/');
        string parent = path.substr(0, slash);
        if (!values.count(parent)) return false;
        values[path] = value;
        return true;
    }

    int get(string path) {
        return values.count(path) ? values[path] : -1;
    }
};

/*
Interview Explanation

Core idea:
A path can be created only if it does not exist and its parent already exists.
Store full paths directly in a hash map.

C++ data structures:
- unordered_map<string,int> maps full path to value.
- The empty string represents the virtual root parent of top-level paths.

Algorithm:
createPath checks duplicate path, extracts parent by the last slash, verifies
parent exists, then inserts the new path.
get returns the stored value or -1.

Correctness:
The map contains exactly created paths plus the virtual root. createPath
enforces both required conditions before insertion, so every stored path is
valid. get directly reflects whether the path was created.

Complexity:
O(L) average time per operation, where L is path length, due to hashing and
parent substring creation. Space is O(number of paths * average path length).

Edge cases:
- Creating an existing path returns false.
- Creating a child before its parent returns false.
- Top-level parent is "" and exists.
*/
