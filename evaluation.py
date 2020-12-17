from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import silhouette_score

def rmse_mae(true, pred):
    """
    Prints RMSE and MAE values of given a prediction and true values
    """
    rmse = mean_squared_error(true,pred,squared=False)

    mae = mean_absolute_error(true,pred)

    print(f'RMSE: {rmse}')
    print(f'MAE:  {mae}\n')

def evaluate_clusters(clusters):
    """
    Evaluates Clustering
    """
    pass