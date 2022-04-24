import numpy as np
import pandas as pd
from collections import Counter
from math import sqrt
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
import sklearn.metrics as metrics
from sklearn.metrics import roc_curve,auc,roc_auc_score,recall_score,precision_score,plot_roc_curve, f1_score

training = pd.read_csv(training_file)
array_training = training.values
X_training = array_training[:,1:10]
y_training = array_training[:,0]
X_train, X_test, y_train, y_test = train_test_split(X_training, y_training, test_size=0.25, random_state = 666, stratify=y_training)

def Find_Optimal_Cutoff(TPR, FPR, threshold):
	y = TPR - FPR
	Youden_index = np.argmax(y)
	optimal_threshold = threshold[Youden_index]
	point = [FPR[Youden_index], TPR[Youden_index]]
	return optimal_threshold, point

def ROC(label, y_prob):
	fpr, tpr, thresholds = roc_curve(label, y_prob, pos_label=1)
	roc_auc = auc(fpr, tpr)
	optimal_th, optimal_point = Find_Optimal_Cutoff(TPR=tpr, FPR=fpr, threshold=thresholds)
	return fpr, tpr, roc_auc, optimal_th, optimal_point

def Evaluation_matrix(row):
	group = row["group"]
	predict = row["predict_group"]
	if group == 0 and predict == 0:
		return "TN"
	if group == 0 and predict == 1:
		return "FP"
	if group == 1 and predict == 1:
		return "TP"
	if group == 1 and predict == 0:
		return "FN"
  
def calculate_MCC(TP_number,FN_number,FP_number,TN_number):
	AA = TP_number
	BB = FN_number
	CC = FP_number
	DD = TN_number
	try:
		Accuracy = (AA+DD)/(AA+BB+CC+DD)
	except ZeroDivisionError:
		Accuracy = float('nan')
	try:
		precision = AA / (AA + CC)
	except ZeroDivisionError:
		precision = float('nan')
	try:
		NPV = DD / (BB + DD)
	except ZeroDivisionError:
		NPV = float('nan')
	try:
		Sensitivity = AA / (AA + BB)
	except ZeroDivisionError:
		Sensitivity= float('nan')
	try:
		Specificity = DD / (CC + DD)
	except ZeroDivisionError:
		Specificity = float('nan')
	try:
		F1 = 2 * precision * Sensitivity / (precision + Sensitivity)
	except ZeroDivisionError:
		F1 = float('nan')
	try:
		numerator = (AA * DD) - (CC * BB)
		denominator = sqrt((AA + CC) * (AA + BB) * (DD + CC) * (DD + BB))
		MCC = numerator/denominator
	except ZeroDivisionError:
		MCC = float('nan')
	return Accuracy, precision, NPV, Sensitivity, Specificity, F1, MCC 

def machine_learning(criterion_option,max_depth_option,min_samples_leaf_option,max_features_option):
	machine_model = tree.DecisionTreeClassifier(criterion= criterion_option, max_depth=max_depth_option, min_samples_leaf=min_samples_leaf_option,max_features=max_features_option,random_state=666,splitter="best",class_weight='balanced')
	machine_model.fit(X_train, y_train)

	# probability_score
	train_file = pd.DataFrame(machine_model.predict_proba(X_train))
	train_file.columns =["negative_score", "pos_score"]
	test_file = pd.DataFrame(machine_model.predict_proba(X_test))
	test_file.columns =["negative_score", "pos_score"]
	training_file = pd.DataFrame(machine_model.predict_proba(X_training))
	training_file.columns =["negative_score", "pos_score"]

	# true_label
	train_file['true_label'] = y_train
	test_file['true_label'] = y_test
	training_file['true_label'] = y_training
	training_file_labels = training_file['true_label']
	training_file_preds = training_file['pos_score']
	training_fpr, training_tpr, training_roc_auc, training_optimal_th, training_optimal_point = ROC(training_file_labels, training_file_preds)

	AAAAA = training_optimal_th
	train_file['predict_group'] = train_file['pos_score'].map(lambda x: 1 if x >= AAAAA else 0)
	train_file['group'] = train_file['true_label']
	train_file['result'] = train_file[['group', 'predict_group']].apply(Evaluation_matrix, axis=1)
	c_train = Counter(train_file['result'])
	train_AA = c_train["TP"]
	train_BB = c_train["FN"]
	train_CC = c_train["FP"]
	train_DD = c_train["TN"]
	train_Accuracy, train_precision, train_NPV, train_Sensitivity, train_Specificity, train_F1, train_MCC = calculate_MCC(train_AA,train_BB,train_CC,train_DD)

	test_file['predict_group'] = test_file['pos_score'].map(lambda x: 1 if x >= AAAAA else 0)
	test_file['group'] = test_file['true_label']
	test_file['result'] = test_file[['group', 'predict_group']].apply(Evaluation_matrix, axis=1)
	c_test = Counter(test_file['result'])
	test_AA = c_test["TP"]
	test_BB = c_test["FN"]
	test_CC = c_test["FP"]
	test_DD = c_test["TN"]
	test_Accuracy, test_precision, test_NPV, test_Sensitivity, test_Specificity, test_F1, test_MCC = calculate_MCC(test_AA, test_BB, test_CC, test_DD)

	training_file['predict_group'] = training_file['pos_score'].map(lambda x: 1 if x >= AAAAA else 0)
	training_file['group'] = training_file['true_label']
	training_file['result'] = training_file[['group', 'predict_group']].apply(Evaluation_matrix, axis=1)
	c_training = Counter(training_file['result'])
	training_AA = c_training["TP"]
	training_BB = c_training["FN"]
	training_CC = c_training["FP"]
	training_DD = c_training["TN"]
	training_Accuracy, training_precision, training_NPV, training_Sensitivity, training_Specificity, training_F1, training_MCC = calculate_MCC(
		training_AA, training_BB, training_CC, training_DD)
	return("%s,%f,%f,%f,%f,%f,%f,%f" % (criterion_option,max_depth_option,min_samples_leaf_option,max_features_option,AAAAA,train_MCC,test_MCC,training_MCC))
  
if __name__ == '__main__':
	result_file = open('1111.csv', 'a')
	result_file_header = "criterion_option,max_depth_option,min_samples_leaf_option,max_features_option,AAAAA,train_MCC,test_MCC,training_MCC\n"
	result_file.write(result_file_header)
	DT_criterion = ["entropy","gini"]
	DT_max_depth = np.arange(3,10,1)
	DT_min_samples_leaf = np.arange(5,251,5)
	DT_max_features = np.arange(3,10,1)

	for criterion_option in DT_criterion:
		for max_depth_option in DT_max_depth:
			for min_samples_leaf_option in DT_min_samples_leaf:
				for max_features_option in DT_max_features:
					machine_result = machine_learning(criterion_option, max_depth_option, min_samples_leaf_option, max_features_option)
					result_file.write(machine_result + "\n")

	result_file.close()