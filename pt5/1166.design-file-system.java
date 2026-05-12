import java.util.*;

class FileSystem {
    private final Map<String, Integer> values;

    public FileSystem() {
        values = new HashMap<>();
        values.put("", -1);
    }

    public boolean createPath(String path, int value) {
        if (values.containsKey(path)) {
            return false;
        }

        String parent = path.substring(0, path.lastIndexOf('/'));
        if (!values.containsKey(parent)) {
            return false;
        }

        values.put(path, value);
        return true;
    }

    public int get(String path) {
        return values.getOrDefault(path, -1);
    }
}

