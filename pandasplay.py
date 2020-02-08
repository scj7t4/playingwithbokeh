import pandas

time = [t / 20 for t in range(1000)]
value = [t % 31 - 15 for t in range(1000)]

t0 = pandas.to_timedelta(time, unit='s')

df = pandas.DataFrame(t0, columns=['time'])
df['value'] = value
df = df.set_index('time')

print(df)

total_time = t0[-1] - t0[0]
print(total_time)

interval = total_time / 50
print(interval)

grouping = df.resample('1s')


def first_sample_time(x):
    return x.index[0]


def first_sample_value(x):
    return x.iloc[0]


def min_sample_time(x):
    return x.idxmin()


def min_sample_value(x):
    return x.iloc[x.argmin()]


def max_sample_time(x):
    return x.idxmax()


def max_sample_value(x):
    return x.iloc[x.argmax()]


def last_sample_time(x):
    return x.index[-1]


def last_sample_value(x):
    return x.iloc[-1]


max_df = grouping \
    .apply([
    first_sample_time,
    first_sample_value,
    min_sample_time,
    min_sample_value,
    max_sample_time,
    max_sample_value,
    last_sample_time,
    last_sample_value
])
# min_df = grouping \
#    .apply(lambda x: x.loc[x['value'].idxmin()])
# first_df = grouping() \
#     .agg(lambda x: x.loc[0])
# last_df = grouping() \
#     .agg(lambda x: x.loc[-1])


# res = pandas.concat([max_df, min_df])

# print(res)
print(max_df)

if __name__ == '__main__':
    pass
