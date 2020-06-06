import glob
import os
import pandas
import matplotlib.pyplot as plt
from study_params import duration_list, criteria_list


# Do not truncate the columns while printing in the console of IDE
pandas.set_option('display.width', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.max_rows', None)


# =======================================================================================================================
def get_price_data_wld(symbol, snapshot_date):
    """
    Get Price Data from WLD
    :param symbol:  AAPL
    :param snapshot_date: Example: 20190524
    :return:
    """
    pricedatafile = 'data/pricedata-{}/{}.csv'.format(snapshot_date, symbol)
    pricedata = pandas.read_csv(pricedatafile, names=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    return pricedata

# =======================================================================================================================
def get_pricedata_ngd(symbol, snapshot_date):
    """
    Get Price Data from NGD. Uses delisted stocks as well.
    :param symbol: AAPL
    :param snapshot_date: 20190524
    :return:
    """
    # First check in ngdata/stocks directory
    pricedatafile = 'data/ngdata/stocks/{}.csv'.format(symbol)
    if not os.path.exists(pricedatafile):
        # Next check in ngdata/stocks-delisted directory
        delistedPattern = 'data/ngdata/stocks-delisted/{}-*.csv'.format(symbol)
        files = glob.glob(delistedPattern)
        if len(files) == 0:
            return None
        # Keeping it simple - if there are two matches, then we are picking the latest one. Ideally, I will like to pick
        # the one which matches closest to the snapshot_date. Something to do sometime later.
        if len(files) > 1:
            files.sort()
        pricedatafile = files[len(files)-1]
    pricedata = pandas.read_csv(pricedatafile)
    return pricedata

# =======================================================================================================================
def find_stats_for_one_criteria_one_score(ms_df, duration, criteria_name, score):
    #find_stats_for_one_rating_number(ms, rating, ratingNumber, d1, d2, d3):
    query = criteria_name + ' == ' + str(score)
    print("Query: [{}]".format(query))
    stock_list_df = ms_df.query(query)
    symbols_col = stock_list_df['Symbol']

    # We need to get advance of every stock in the bucket
    stock_stats_df = pandas.DataFrame(columns=['Symbol', 'Advance', duration['start_date'], duration['end_date']])
    skipped_symbols = []
    for symbol in symbols_col:
        # print(symbol)
        try:
            pricedata = get_price_data_wld(symbol, duration['pricedata_date'])
            p1 = pricedata.query('Date==' + duration['start_date'])['Open'].item()
            p2 = pricedata.query('Date==' + duration['end_date'])['Open'].item()
        except:
            # Skip if the data is missing or has issues
            # print("    ==> SKIPPING")
            skipped_symbols.append(symbol)
            continue
        advance = 100 * (p2 - p1) / p1
        stock_stats_df = stock_stats_df.append({
            'Symbol': symbol,
            'Advance': advance,
            duration['start_date']: p1,
            duration['end_date']: p2,
        }, ignore_index=True)
        # print("    {}, {} = {}, {} = {}, {} = {}, {}, {}, {}\n".format(symbol, d1, p1, d2, p2, d3, p3, correction, advance, recovery))

    print("Stats for Stock List for Query[{}]".format(query), stock_stats_df, sep='\n')
    print("\nStat Summary for the Stock List:")
    print(stock_stats_df.describe())
    print("\nSkipped Symbols: {}".format(skipped_symbols))
    #stock_stats_df.to_csv('data/{}_{}.csv'.format(criteria_name, score))

    return stock_stats_df['Advance'].mean()


# =======================================================================================================================
def find_plot_data_one_criteria(ms, duration, criteria):

    # rating_stats stores stats for criteria with one row for a score bucket
    rating_stats = pandas.DataFrame(columns=[criteria['display_name'], 'Avg. Advance'])
    for score in criteria['score_buckets']:
        print("\n------------------------------ {} - {} [{}] ------------------------------".
              format(duration['display_name'], criteria['display_name'], score))
        avg_advance = find_stats_for_one_criteria_one_score(ms, duration, criteria['criteria_name'], score)
        rating_stats = rating_stats.append({
            criteria['display_name']: score,
            'Avg. Advance': avg_advance,
        }, ignore_index=True)

        # For logging purpose only
        print("\nInteresting stat:")
        print(rating_stats.query("`{}` == {}".format(criteria['display_name'], str(score))))

    print("\n------------------------------ {} - {} Study Summary ------------------------------\n".
          format(duration['display_name'], criteria['criteria_name']))
    print(rating_stats)

    # Save stats to CSV file for later processing
    out_csv_file = 'results/stats-{}-{}.csv'.format(duration['display_name'], criteria['criteria_name'])
    print("Writing to {}".format(out_csv_file))
    rating_stats.to_csv(out_csv_file)

    # save plot of stats to PNG fie for immediate observation
    out_png_file = "results/plot-{}-{}.png".format(duration['display_name'], criteria['criteria_name'])
    title = "{} / {} Vs Price Change %".format(duration['display_name'], criteria['display_name'])
    ax = rating_stats.plot(title=title, x=criteria['display_name'], y="Avg. Advance", figsize=(15, 9), grid=True, legend=True)
    ax.set_ylabel("Price Change %")
    ax.set_xlabel(criteria['display_name'])
    print("Saving plot. Filename: {}".format(out_png_file))
    plt.savefig(out_png_file)
    # Close the figures, otherwise they are kept in memory
    plt.close('all')

# =======================================================================================================================
def study_all():
    # Make sure output directories are created.
    if not os.path.exists("results"):
        os.mkdir("results")

    # For each duration, plot each criteria.
    for duration in duration_list:
        msdata_file = "data/msdata/{}-ms.csv".format(duration['msdata_date'])
        ms = pandas.read_csv(msdata_file, index_col=0)
        ms.rename(columns={
            'EPS Rating': 'EPSRating',
            'RS Rating': 'RSRating',
            'SMR Rating': 'SMRRating',
            'A/D Rating': 'ADRating',
            'Comp Rating': 'CompRating',
            'Ind Group RS': 'IndGroupRS',
        }, inplace=True)
        for criteria in criteria_list:
            find_plot_data_one_criteria(ms, duration, criteria)


# =======================================================================================================================
if __name__ == "__main__":
    print("Started study...")
    study_all()
    print("\nFinished study!")
