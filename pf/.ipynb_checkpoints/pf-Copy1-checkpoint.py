import pandas as pd
from itertools import combinations

def compute_pairwise_differences(df):
    """Compute the pairwise differences in total reads."""
    pairs = list(combinations(df['Pool'], 2))
    differences = []
    for pair in pairs:
        reads1 = df[df['Pool'] == pair[0]]['Total Reads'].values[0]
        reads2 = df[df['Pool'] == pair[1]]['Total Reads'].values[0]
        differences.append((pair[0], pair[1], abs(reads1 - reads2)))
    return differences

def generate_combinations(differences):
    """Generate all possible combinations of pairs ensuring unique pools."""
    return list(combinations(differences, 2))

def find_best_combination(combinations):
    """Find the best combination with the lowest difference between differences."""
    best_combination = None
    best_difference = float('inf')
    for comb in combinations:
        pools = {comb[0][0], comb[0][1], comb[1][0], comb[1][1]}
        if len(pools) == 4:
            diff1 = comb[0][2]
            diff2 = comb[1][2]
            difference_between_differences = abs(diff1 - diff2)
            if difference_between_differences < best_difference:
                best_difference = difference_between_differences
                best_combination = comb
    return best_combination, best_difference

def find_lowest_difference_pair(differences):
    """Find the pair with the lowest difference."""
    return min(differences, key=lambda x: x[2])

def find_remaining_pair(df, pair):
    """Find the difference for the remaining pair of pools."""
    remaining_pools = set(df['Pool']) - {pair[0], pair[1]}
    if not remaining_pools:
        return None  # No remaining pairs
    remaining_pair = tuple(remaining_pools)
    reads1 = df[df['Pool'] == remaining_pair[0]]['Total Reads'].values[0]
    reads2 = df[df['Pool'] == remaining_pair[1]]['Total Reads'].values[0]
    remaining_difference = abs(reads1 - reads2)
    return remaining_pair + (remaining_difference,)

def compute_reads_ratio(df, pair):
    """Compute the ratio of total reads between two pools."""
    reads1 = df[df['Pool'] == pair[0]]['Total Reads'].values[0]
    reads2 = df[df['Pool'] == pair[1]]['Total Reads'].values[0]
    ratio = reads1 / reads2 if reads2 != 0 else float('inf')
    return ratio

def lowest_difference(df):
    """Main function to compute the lowest difference pairs, remaining pair difference, and ratios."""
    differences = compute_pairwise_differences(df)
    if len(differences) == 1:
        # Only one pair available
        lowest_diff_pair = differences[0]
        lowest_diff_pair_ratio = compute_reads_ratio(df, lowest_diff_pair[:2])
        lowest_diff_pair_inverse_ratio = compute_reads_ratio(df, (lowest_diff_pair[1], lowest_diff_pair[0]))

        reads1 = df[df['Pool'] == lowest_diff_pair[0]]['Total Reads'].values[0]
        reads2 = df[df['Pool'] == lowest_diff_pair[1]]['Total Reads'].values[0]

        result_data = [
            (lowest_diff_pair[0], lowest_diff_pair[1], reads1, lowest_diff_pair_ratio),
            (lowest_diff_pair[1], lowest_diff_pair[0], reads2, lowest_diff_pair_inverse_ratio)
        ]

        result_df = pd.DataFrame(result_data, columns=['Pool 1', 'Pool 2', 'Total Reads', 'Ratio'])
        return result_df

    lowest_diff_pair = find_lowest_difference_pair(differences)
    remaining_diff_pair = find_remaining_pair(df, lowest_diff_pair)

    lowest_diff_pair_ratio = compute_reads_ratio(df, lowest_diff_pair[:2])
    remaining_diff_pair_ratio = compute_reads_ratio(df, remaining_diff_pair[:2]) if remaining_diff_pair else None

    lowest_diff_pair_inverse_ratio = compute_reads_ratio(df, (lowest_diff_pair[1], lowest_diff_pair[0]))
    remaining_diff_pair_inverse_ratio = compute_reads_ratio(df, (remaining_diff_pair[1], remaining_diff_pair[0])) if remaining_diff_pair else None

    reads1 = df[df['Pool'] == lowest_diff_pair[0]]['Total Reads'].values[0]
    reads2 = df[df['Pool'] == lowest_diff_pair[1]]['Total Reads'].values[0]

    result_data = [
        (lowest_diff_pair[0], lowest_diff_pair[1], reads1, lowest_diff_pair_ratio),
        (lowest_diff_pair[1], lowest_diff_pair[0], reads2, lowest_diff_pair_inverse_ratio)
    ]

    if remaining_diff_pair:
        reads3 = df[df['Pool'] == remaining_diff_pair[0]]['Total Reads'].values[0]
        reads4 = df[df['Pool'] == remaining_diff_pair[1]]['Total Reads'].values[0]
        result_data.extend([
            (remaining_diff_pair[0], remaining_diff_pair[1], reads3, remaining_diff_pair_ratio),
            (remaining_diff_pair[1], remaining_diff_pair[0], reads4, remaining_diff_pair_inverse_ratio)
        ])

    result_df = pd.DataFrame(result_data, columns=['Pool 1', 'Pool 2', 'Total Reads', 'Ratio'])
    return result_df

def lowest_second_order_difference(df):
    """Main function to find the lowest difference pairs and compute ratios."""
    differences = compute_pairwise_differences(df)
    if len(differences) <= 1:
        return pd.DataFrame(columns=['Pool 1', 'Pool 2', 'Total Reads', 'Ratio'])  # Not enough pairs to compare

    combs = generate_combinations(differences)
    best_combination, best_difference = find_best_combination(combs)

    result_data = []
    for pair in best_combination:
        ratio = compute_reads_ratio(df, pair[:2])
        inverse_ratio = compute_reads_ratio(df, (pair[1], pair[0]))
        reads1 = df[df['Pool'] == pair[0]]['Total Reads'].values[0]
        reads2 = df[df['Pool'] == pair[1]]['Total Reads'].values[0]
        result_data.append((pair[0], pair[1], reads1, ratio))
        result_data.append((pair[1], pair[0], reads2, inverse_ratio))

    result_df = pd.DataFrame(result_data, columns=['Pool 1', 'Pool 2', 'Total Reads', 'Ratio']).sort_values(by='Pool 1')
    return result_df

def generate_read_adj_table(df):
    return pd.concat([lowest_difference(df), lowest_second_order_difference(df)], axis=0)

# Example dataframe
data = {
    'Pool': ['SALK111', 'SALK112', 'SALK113', 'SALK114'],
    'Total Reads': [1377429, 913826, 1164538, 1161348]
}
df_example = pd.DataFrame(data)

# Use the function
result_df = generate_read_adj_table(df_example)
print(result_df)
