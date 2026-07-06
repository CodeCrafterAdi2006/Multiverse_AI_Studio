# Skill: Recommender Systems with Collaborative Filtering

## Purpose
To build recommendation systems using collaborative filtering techniques for personalized user experiences.

## When to Use
- When building product recommendations for e-commerce
- For movie/music/content recommendations
- When personalizing user experiences
- For "Customers who bought this also bought" features
- When you have user-item interaction data

## Procedure

### 1. User-Based Collaborative Filtering
Recommend items based on similar users.

```python
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Sample user-item ratings matrix
ratings_data = {
    'User1': [5, 4, 0, 0, 3],
    'User2': [0, 5, 4, 0, 0],
    'User3': [4, 0, 5, 3, 0],
    'User4': [0, 0, 4, 5, 4],
    'User5': [3, 0, 0, 4, 5]
}
items = ['ItemA', 'ItemB', 'ItemC', 'ItemD', 'ItemE']

ratings_matrix = pd.DataFrame(ratings_data, index=items).T

def user_based_cf(user_id, ratings_matrix, n_recommendations=3):
    # Calculate user similarity
    user_similarity = cosine_similarity(ratings_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=ratings_matrix.index, columns=ratings_matrix.index)
    
    # Get similar users
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:]
    
    # Predict ratings
    user_ratings = ratings_matrix.loc[user_id]
    predicted_ratings = pd.Series(dtype='float64')
    
    for item in ratings_matrix.columns:
        if user_ratings[item] == 0:
            weighted_sum = 0
            similarity_sum = 0
            for similar_user in similar_users.index:
                if ratings_matrix.loc[similar_user, item] > 0:
                    weighted_sum += similar_users[similar_user] * ratings_matrix.loc[similar_user, item]
                    similarity_sum += similar_users[similar_user]
            if similarity_sum > 0:
                predicted_ratings[item] = weighted_sum / similarity_sum
    
    return predicted_ratings.sort_values(ascending=False).head(n_recommendations)

# Usage
recommendations = user_based_cf('User1', ratings_matrix)
print("Recommendations for User1:", recommendations)
```

### 2. Item-Based Collaborative Filtering
Recommend items similar to those the user liked.

```python
def item_based_cf(user_id, ratings_matrix, n_recommendations=3):
    # Calculate item similarity
    item_similarity = cosine_similarity(ratings_matrix.T)
    item_similarity_df = pd.DataFrame(item_similarity, index=ratings_matrix.columns, columns=ratings_matrix.columns)
    
    user_ratings = ratings_matrix.loc[user_id]
    predicted_ratings = pd.Series(dtype='float64')
    
    for item in ratings_matrix.columns:
        if user_ratings[item] == 0:
            weighted_sum = 0
            similarity_sum = 0
            for rated_item in user_ratings.index:
                if user_ratings[rated_item] > 0:
                    weighted_sum += item_similarity_df[item][rated_item] * user_ratings[rated_item]
                    similarity_sum += item_similarity_df[item][rated_item]
            if similarity_sum > 0:
                predicted_ratings[item] = weighted_sum / similarity_sum
    
    return predicted_ratings.sort_values(ascending=False).head(n_recommendations)
```

### 3. Matrix Factorization with SVD
Use Singular Value Decomposition for better recommendations.

```python
from scipy.sparse.linalg import svds

def svd_recommender(ratings_matrix, user_id, n_recommendations=3, n_factors=2):
    # Convert to numpy array and center
    ratings = ratings_matrix.values
    user_ratings_mean = np.mean(ratings, axis=1)
    ratings_demeaned = ratings - user_ratings_mean.reshape(-1, 1)
    
    # Perform SVD
    U, sigma, Vt = svds(ratings_demeaned, k=n_factors)
    sigma = np.diag(sigma)
    
    # Reconstruct ratings
    predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    predicted_ratings_df = pd.DataFrame(predicted_ratings, index=ratings_matrix.index, columns=ratings_matrix.columns)
    
    # Get recommendations
    user_ratings = ratings_matrix.loc[user_id]
    recommendations = predicted_ratings_df.loc[user_id][user_ratings == 0].sort_values(ascending=False).head(n_recommendations)
    
    return recommendations
```

### 4. Using Surprise Library
Use the Surprise library for recommendation systems.

```python
from surprise import Dataset, Reader, SVD, KNNBasic
from surprise.model_selection import train_test_split
from surprise.metrics import accuracy

# Load data
ratings_dict = {
    'userID': [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
    'itemID': [1, 2, 3, 1, 2, 4, 2, 3, 4, 1, 3, 4],
    'rating': [5, 4, 3, 5, 4, 4, 4, 5, 5, 3, 5, 4]
}

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(pd.DataFrame(ratings_dict)[['userID', 'itemID', 'rating']], reader)

# Split data
trainset, testset = train_test_split(data, test_size=0.25)

# Train SVD model
algo = SVD()
algo.fit(trainset)

# Test
predictions = algo.test(testset)
print("RMSE:", accuracy.rmse(predictions))

# Get recommendations for a user
def get_surprise_recommendations(algo, user_id, item_ids, n_recommendations=3):
    predictions = []
    for item_id in item_ids:
        pred = algo.predict(user_id, item_id)
        predictions.append((item_id, pred.est))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:n_recommendations]
```

### 5. Hybrid Recommender
Combine collaborative filtering with content-based filtering.

```python
def hybrid_recommender(user_id, ratings_matrix, item_features, n_recommendations=3):
    # Get collaborative filtering recommendations
    cf_recs = user_based_cf(user_id, ratings_matrix, n_recommendations=5)
    
    # Get content-based recommendations (using item features)
    item_similarity = cosine_similarity(item_features)
    user_rated_items = ratings_matrix.loc[user_id][ratings_matrix.loc[user_id] > 0].index
    
    content_recs = pd.Series(dtype='float64')
    for item in ratings_matrix.columns:
        if item not in user_rated_items:
            sim_sum = 0
            for rated_item in user_rated_items:
                sim_sum += item_similarity[list(ratings_matrix.columns).index(item)][list(ratings_matrix.columns).index(rated_item)]
            content_recs[item] = sim_sum / len(user_rated_items)
    
    content_recs = content_recs.sort_values(ascending=False).head(5)
    
    # Combine recommendations (simple average)
    combined_recs = pd.Series(dtype='float64')
    for item in set(cf_recs.index).union(set(content_recs.index)):
        cf_score = cf_recs.get(item, 0)
        content_score = content_recs.get(item, 0)
        combined_recs[item] = (cf_score + content_score) / 2
    
    return combined_recs.sort_values(ascending=False).head(n_recommendations)
```

## Best Practices
- **Data Preprocessing**: Clean and preprocess your data thoroughly
- **Cold Start**: Handle new users/items with hybrid approaches
- **Evaluation**: Use RMSE, MAE, or ranking metrics (NDCG, MAP)
- **Scalability**: Use matrix factorization or deep learning for large datasets
- **Diversity**: Ensure recommendations are diverse, not just similar
- **Freshness**: Update recommendations regularly with new data
- **A/B Testing**: Always test recommendations with real users
- **Privacy**: Be mindful of user privacy and data usage
