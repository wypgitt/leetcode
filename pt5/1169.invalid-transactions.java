import java.util.*;

class Solution {
    public List<String> invalidTransactions(String[] transactions) {
        Transaction[] parsed = new Transaction[transactions.length];
        Map<String, List<Integer>> byName = new HashMap<>();
        boolean[] invalid = new boolean[transactions.length];

        for (int i = 0; i < transactions.length; i++) {
            String[] parts = transactions[i].split(",");
            parsed[i] = new Transaction(parts[0], Integer.parseInt(parts[1]), Integer.parseInt(parts[2]), parts[3]);
            byName.computeIfAbsent(parts[0], key -> new ArrayList<>()).add(i);
            if (parsed[i].amount > 1000) {
                invalid[i] = true;
            }
        }

        for (List<Integer> indices : byName.values()) {
            for (int i = 0; i < indices.size(); i++) {
                for (int j = i + 1; j < indices.size(); j++) {
                    int aIndex = indices.get(i);
                    int bIndex = indices.get(j);
                    Transaction a = parsed[aIndex];
                    Transaction b = parsed[bIndex];
                    if (Math.abs(a.time - b.time) <= 60 && !a.city.equals(b.city)) {
                        invalid[aIndex] = true;
                        invalid[bIndex] = true;
                    }
                }
            }
        }

        List<String> answer = new ArrayList<>();
        for (int i = 0; i < transactions.length; i++) {
            if (invalid[i]) {
                answer.add(transactions[i]);
            }
        }
        return answer;
    }

    private static class Transaction {
        String name;
        int time;
        int amount;
        String city;

        Transaction(String name, int time, int amount, String city) {
            this.name = name;
            this.time = time;
            this.amount = amount;
            this.city = city;
        }
    }
}

