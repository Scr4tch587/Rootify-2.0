import pandas as pd

df = pd.read_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_data.csv', names=['id', 'input_text', 'label', 'bucket'], index_col = 'id')

positive_df = df[df['bucket']=='positive'].sample(frac=1, random_state=42).copy()
validation = positive_df.iloc[0:32].copy()
testing = positive_df.iloc[32:64].copy()
training = positive_df.iloc[64:].copy()

quantities = [27, 18, 18, 9, 9, 9]
buckets = ["reverse_direction", "non_agent", "comparison_only", "naming_etymology", "journalist_actor", "malformed_span"]

for i in range(len(buckets)):
    bucket = buckets[i]
    quantity = quantities[i]
    bucket_df = df[df['bucket']==bucket].sample(frac=1, random_state=42).copy()
    validation=pd.concat([validation, bucket_df.iloc[0:quantity]])
    testing=pd.concat([testing, bucket_df.iloc[quantity:2*quantity]])
    training=pd.concat([training, bucket_df.iloc[2*quantity:]])
validation.to_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_validation.csv')
testing.to_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_testing.csv')
training.to_csv('/Users/scr4tch/Documents/Coding/Projects/Rootify2/rootify/api/app/pipeline/scoring/ml_scorer/wikipedia_training.csv')