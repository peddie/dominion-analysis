import pandas as pd
import numpy as np
from statsmodels.api import OLS


score_column_names = ['Matt rating', 'Vera Rating']

game_name_rows = ['Original Set', 'Prosperity', 'Seaside']

set_row_cutoff = 5
metadata_cutoff = 6
currency_cutoff = metadata_cutoff + 1
victory_cutoff = currency_cutoff + 1


def load(filename):
    """
    Load and normalize the Dominion database.  Each column in 'cards'
    is a card; each row in 'cards' is a game.  Each column in
    'metadata' is a metadata category; each row in 'metadata' is a
    game.

    """
    csv = pd.read_csv(filename)

    # Extract the metadata columns -- these don't correspond to cards.
    metadata_indices = csv.ix[0, :metadata_cutoff]
    metadata = pd.DataFrame(csv.iloc[set_row_cutoff:,
                                     :metadata_cutoff].apply(pd.to_numeric,
                                                             errors='ignore').values,
                            index=xrange(csv.shape[0] - set_row_cutoff),
                            columns=metadata_indices)

    # Record which game each column is in.
    game_sets = {}
    for game_row in xrange(0, 3):
        for col in csv.ix[0, csv.ix[game_row + 1, :] == '1']:
            game_sets[col] = game_name_rows[game_row]

    # Compute a new multi-index containing the game labels for each
    # card.
    action_indices = [('action', game_sets[card], card)
                      for card in csv.ix[0, :] if card in game_sets.keys()]
    currency_indices = [('currency', 'Prosperity', name)
                        for name in csv.ix[0,
                                           metadata_cutoff:currency_cutoff]]
    victory_indices = [('victory', 'Prosperity', name)
                       for name in csv.ix[0,
                                          currency_cutoff:victory_cutoff]]

    cards = pd.DataFrame(csv.iloc[set_row_cutoff:,
                                  metadata_cutoff:].apply(pd.to_numeric,
                                                          errors='ignore').values,
                         index=xrange(csv.shape[0] - set_row_cutoff),
                         columns=pd.MultiIndex.from_tuples(currency_indices
                                                           + victory_indices
                                                           + action_indices,
                                                           names=['type',
                                                                  'set',
                                                                  'card']))

    cards.sort_index(inplace=True, axis=1)
    return cards, metadata


def display_scores(scores, label):
    """
    Display a dictionary of label-score pairs in descending order.
    """
    ordered_scores = sorted(scores.items(),
                            key=lambda x: x[1] if np.isfinite(x[1])
                            else float('-inf'),
                            reverse=True)
    name_column_size = max([len(s[0]) for s in ordered_scores])

    equal_pad = max(name_column_size, len("    Scores by " + label))
    print "=" * equal_pad
    print "    Scores by", label

    omitted = []
    for name, score in ordered_scores:
        if not np.isfinite(score):
            omitted.append(name)
            continue
        print "%s%s  " % (name, " " * (name_column_size - len(name))), score

    if len(omitted) > 0:
        print "Omitted due to lack of data:"
        print "   ", omitted


def card_score(cards, metadata, card_name, score_columns=score_column_names):
    """
    Compute an average score for an individual card.
    """
    idx = pd.IndexSlice[:, :, card_name]
    count = cards.loc[:, idx].count().values
    if count < 1:
        return np.nan

    if np.sum(cards.loc[:, idx])[0] == 0:
        return np.nan

    return np.mean([np.sum(cards.loc[:, idx].multiply(
        metadata.loc[:, col].apply(pd.to_numeric, errors='ignore'),
        axis=0)).values / count
                    for col in score_columns])


def card_scores(cards, metadata):
    """
    Calculate and display scores for all action cards.
    """
    display_scores({col: card_score(cards, metadata, col)
                    for col in cards['action'].columns.get_level_values(1)},
                   "card type")


def set_score(cards, metadata, set_name, score_columns=score_column_names):
    """
    Compute an average score for a game set.
    """
    idx = pd.IndexSlice[:, set_name, :]
    count = np.sum(cards.loc[:, idx].count())
    if count < 1:
        return np.nan

    if np.sum(np.sum(cards.loc[:, idx])[0]) == 0:
        return np.nan

    return np.mean([np.sum(np.sum(cards.loc[:, idx].multiply(
        metadata.loc[:, col].apply(pd.to_numeric, errors='ignore'),
        axis=0))) / count
                    for col in score_columns])


def set_scores(cards, metadata):
    """
    Calculate and display scores for all game sets.
    """
    display_scores({s: set_score(cards, metadata, s)
                    for s in set(cards['action'].columns.get_level_values(0))},
                   "Dominion set")


def set_score_regression(cards, metadata, score_columns=score_column_names):
    """
    Perform a linear regression to determine the degree to which each
    game set's action cards contribute to a good score.
    """
    sets = set(cards['action'].columns.get_level_values(0))
    scores = np.mean(metadata.loc[:, tuple(score_columns)], axis=1)

    # Ignore missing cells
    refine_idx = np.isfinite(scores)
    scores = scores[refine_idx]

    set_counts = pd.concat(
        [pd.DataFrame(np.sum(cards.loc[refine_idx, pd.IndexSlice[:, s, :]],
                             axis=1),
                      columns=[s])
         for s in sets],
        axis=1).fillna(0)

    results = OLS(scores, set_counts).fit()
    print results.summary()


def prosperity_score_regression(cards, metadata,
                                score_columns=score_column_names):
    """
    Perform a linear regression to determine the degree to which the
    Prosperity add-on treasure and victory cards contribute to a good
    score.
    """
    prosperity = set(cards['currency'].columns.get_level_values(1))
    # victory_cards = set(cards['victory'].columns.get_level_values(1))
    # cards = currency_cards.union(victory_cards)
    scores = np.mean(metadata.loc[:, tuple(score_columns)], axis=1)

    # Ignore missing cells
    refine_idx = np.isfinite(scores)
    scores = scores[refine_idx]

    set_counts = pd.concat([pd.DataFrame(cards.loc[refine_idx,
                                                   pd.IndexSlice[:,
                                                                 :,
                                                                 c]].values,
                                         columns=[c])
                            for c in prosperity]
                           + [pd.DataFrame(np.ones((scores.size, 1)),
                                           columns=['Average game score'])],
                           axis=1).fillna(0)

    results = OLS(scores, set_counts).fit()
    print results.summary()

if __name__ == '__main__':
    cards, metadata = load("dominion.csv")

    card_scores(cards, metadata)
    set_scores(cards, metadata)
    set_score_regression(cards, metadata)
    prosperity_score_regression(cards, metadata)
