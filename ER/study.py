import pandas as pd

# Do not truncate the columns while printing in the console of IDE
pd.set_option('display.width', 150)
pd.set_option('display.max_columns', 150)


# =====================================================================================

def find_stats_for_one_rating_number(ms, rating, ratingNumber, d1, d2, d3):
    query = rating + ' == ' + str(ratingNumber)
    print("Query: [{}]".format(query))
    er_stock_list = ms.query(query)
    symbols = er_stock_list['Symbol']
    stock_stats = pd.DataFrame(columns=['Symbol', 'Correction', 'Advance', 'Recovery', d1, d2, d3])
    skipped_symbols = []
    for symbol in symbols:
        # print(symbol)
        try:
            pricedata = pd.read_csv('pricedata/' + symbol + '.csv',
                                    names=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            p1 = pricedata.query('Date==' + d1)['Close'].item()
            p2 = pricedata.query('Date==' + d2)['Close'].item()
            p3 = pricedata.query('Date==' + d3)['Close'].item()
        except:
            # Skip if the data is missing or has issues
            # print("    ==> SKIPPING")
            skipped_symbols.append(symbol)
            continue
        correction = 100 * (p2 - p1) / p1
        advance = 100 * (p3 - p2) / p2
        recovery = 100 * (p3 - p1) / p1
        stock_stats = stock_stats.append({
            'Symbol': symbol,
            'Correction': correction,
            'Advance': advance,
            'Recovery': recovery,
            d1: p1,
            d2: p2,
            d3: p3,
        }, ignore_index=True)
        # print("    {}, {} = {}, {} = {}, {} = {}, {}, {}, {}\n".format(symbol, d1, p1, d2, p2, d3, p3, correction, advance, recovery))

    print("Stats for Stock List for Query[{}]".format(query), stock_stats, sep='\n')
    print("\nStat Summary for the Stock List:")
    print(stock_stats.describe())
    print("\nSkipped Symbols: {}".format(skipped_symbols))

    return (stock_stats['Correction'].mean(), stock_stats['Correction'].max(), stock_stats['Correction'].min(),
            stock_stats['Advance'].mean(), stock_stats['Advance'].max(), stock_stats['Advance'].min(),
            stock_stats['Recovery'].mean(), stock_stats['Recovery'].max(), stock_stats['Recovery'].min(),
            )


# =======================================================================================================================
def find_stats_for_one_rating_range(ms, rating, start_rating_number, end_rating_number, d1, d2, d3):
    rating_stats = pd.DataFrame(columns=[rating, 'Avg.Correction', 'Max.Correction', 'Min.Correction',
                                         'Avg.Advance', 'Max.Advance', 'Min.Advance', 'Avg.Recovery', 'Max.Recovery',
                                         'Min.Recovery'])
    for rating_number in range(start_rating_number, end_rating_number):
        print("\n------------------------------ {} [{}] ------------------------------".format(rating, rating_number))
        (corr_avg, corr_max, corr_min, adv_avg, adv_max, adv_min, recovery_avg, recovery_max, recovery_min) = \
            find_stats_for_one_rating_number(ms, rating, rating_number, d1, d2, d3)
        rating_stats = rating_stats.append({
            rating: rating_number,
            'Avg.Correction': corr_avg,
            'Max.Correction': corr_max,
            'Min.Correction': corr_min,
            'Avg.Advance': adv_avg,
            'Max.Advance': adv_max,
            'Min.Advance': adv_min,
            'Avg.Recovery': recovery_avg,
            'Max.Recovery': recovery_max,
            'Min.Recovery': recovery_min,
        }, ignore_index=True)

        # For logging purpose only
        print("\nInteresting stat:")
        print(rating_stats.query(rating + '==' + str(rating_number)))

    print("\n------------------------------ {} Study Summary ------------------------------\n".format(rating))
    print(rating_stats)
    rating_stats.to_csv(rating + '_stats.csv')


# =======================================================================================================================
def study_all(ms):
    ms.rename(columns={
        'EPS Rating': 'ER',
        'RS Rating': 'RS',
        'SMR Rating': 'SMR',
        'A/D Rating': 'AD',
        'Comp Rating': 'CR',
        'Ind Group RS': 'IndGroupRS',
    }, inplace=True)
    d1 = '20200219'
    d2 = '20200323'
    d3 = '20200528'
    find_stats_for_one_rating_range(ms, "ER", 1, 100, d1, d2, d3)


# =======================================================================================================================
def run():
    # ms = pd.read_excel('msdata/2020-02-19-ms.xlsx', index_col=0)
    ms = pd.read_csv('msdata/2020-02-19-ms.csv', index_col=0)
    study_all(ms)


# =======================================================================================================================
if __name__ == "__main__":
    print("Started study...")
    run()
    print("\nFinished study!")
