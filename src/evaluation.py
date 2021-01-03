from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import silhouette_score

from math import sqrt
from numpy import array
from numpy import mean
from numpy import std
from pandas import DataFrame
from pandas import concat
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import TimeDistributed
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from matplotlib import pyplot

def rmse_mae(true, pred):
    """
    Prints RMSE and MAE values of given a prediction and true values
    """
    rmse = mean_squared_error(true,pred,squared=False)

    mae = mean_absolute_error(true,pred)

    print(f'RMSE: {rmse}')
    print(f'MAE:  {mae}\n')

### Walk-forward Validation Functions###
# Adapted from Machine Learning Mastery
# https://machinelearningmastery.com/how-to-develop-deep-learning-models-for-univariate-time-series-forecasting/

# transform list into supervised learning format
def series_to_supervised(data, n_in=1, n_out=1):
	df = DataFrame(data)
	cols = list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
	# put it all together
	agg = concat(cols, axis=1)
	# drop rows with NaN values
	agg.dropna(inplace=True)
	return agg.values

# root mean squared error or rmse
def measure_rmse(actual, predicted):
	return sqrt(mean_squared_error(actual, predicted))

def measure_mae(actual,predicted):
	return mean_absolute_error(actual,predicted)

# fit a model
def model_fit(train, config):
	# unpack config
	n_seq, n_steps, n_filters, n_kernel, n_nodes, n_epochs, n_batch = config
	n_input = n_seq * n_steps
	# prepare data
	data = series_to_supervised(train, n_in=n_input)
	train_x, train_y = data[:, :-1], data[:, -1]
	train_x = train_x.reshape((train_x.shape[0], n_seq, n_steps, 1))
	# define model
	model = Sequential()
	model.add(TimeDistributed(Conv1D(filters=n_filters, kernel_size=n_kernel, activation='relu', input_shape=(None,n_steps,1))))
	model.add(TimeDistributed(Conv1D(filters=n_filters, kernel_size=n_kernel, activation='relu')))
	model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
	model.add(TimeDistributed(Flatten()))
	model.add(LSTM(n_nodes, activation='relu'))
	model.add(Dense(n_nodes, activation='relu'))
	model.add(Dense(1))
	model.compile(loss='mse', optimizer='adam')
	# fit
	model.fit(train_x, train_y, epochs=n_epochs, batch_size=n_batch, verbose=0)
	return model

# forecast with a pre-fit model
def model_predict(model, history, config):
	# unpack config
	n_seq, n_steps, _, _, _, _, _ = config
	n_input = n_seq * n_steps
	# prepare data
	x_input = array(history[-n_input:]).reshape((1, n_seq, n_steps, 1))
	# forecast
	yhat = model.predict(x_input, verbose=0)
	return yhat[0]

# walk-forward validation for univariate data
def walk_forward_validation(train,test, n_test, cfg):
	predictions = list()
	# split dataset
	# fit model
	model = model_fit(train, cfg)
	# seed history with training dataset
	history = [x for x in train]
	# step over each time-step in the test set
	for i in range(len(test)):
		# fit model and make forecast for history
		yhat = model_predict(model, history, cfg)
		# store forecast in list of predictions
		predictions.append(yhat)
		# add actual observation to history for the next loop
		history.append(test[i])
	# estimate prediction error
	rmse = measure_rmse(test, predictions)
	mae = measure_mae(test,predictions)
	print(f'> RMSE: {round(rmse,3)} \t MAE: {round(mae,3)}')
	return (rmse, mae)

# repeat evaluation of a config
def repeat_evaluate(train, test, config, n_test, n_repeats=30):
	# fit and evaluate the model n times
	scores = [walk_forward_validation(train, test, n_test, config) for _ in range(n_repeats)]
	return array(scores)

# summarize model performance
def summarize_scores(name, scores):
	# print a summary
	mean_rmse, std_rmse = mean(scores[:,0]), std(scores[:,0])
	mean_mae, std_mae = mean(scores[:,1]), std(scores[:,1])
	print('%s: %.3f RMSE (+/- %.3f)' % (name, mean_rmse, std_rmse))
	print('%s: %.3f MAE (+/- %.3f)' % (name, mean_mae, std_mae))
	# box and whisker plot
	pyplot.boxplot(scores)
	pyplot.show()