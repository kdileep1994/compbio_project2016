#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  3 19:48:21 2016

@author: Manu
"""

# Random Forest Classification
import pandas as pd
import warnings
from sklearn.model_selection import cross_val_score
#from sklearn.model_selection import cross_val_predict
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
import math
import numpy as np
#from sklearn.metrics import classification_report
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import make_scorer
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn

def prepare_data_for_classifier(feature_path, labelled_path, randomize = False, only_columns = None):
    # We read the files
    features_data = pd.read_csv(feature_path)
    labelled_data = pd.read_csv(labelled_path)

    # Filter unwanted features
    if only_columns is not None:
        features_data = features_data[only_columns]

    # We save the features names
    headers = list(features_data.columns)
        
    #Randomize dataset    
    if randomize :
        rd_index = np.random.permutation(features_data.index)
        features_data = features_data.reindex(rd_index)
        labelled_data = labelled_data.reindex(rd_index)

    # Scikit uses arrays, so we convert the dataframes 
    labels_array = np.array(labelled_data['label'], dtype=int)
    feature_array = features_data.as_matrix()
    return (feature_array, labels_array, headers)    
    
def run_classifier(feature_path, labelled_path):
    training_data = pd.read_csv(feature_path)
    labelled_data = pd.read_csv(labelled_path)
    feature_df = training_data
    headers = feature_df.columns
    labels_df = np.array(labelled_data['label'], dtype=int)
    feature_df = feature_df.as_matrix()
    num_trees = 100
    max_features = int(math.sqrt(feature_df.shape[1]))
    model = RandomForestClassifier(n_estimators=num_trees, max_features=max_features)
    dummy_model = DummyClassifier(constant=None, random_state=0, strategy='most_frequent')
    scores = cross_val_score(model, feature_df , labels_df, cv=ShuffleSplit(n_splits=3, train_size=0.7, random_state=0))
    # scores = cross_val_score(model, feature_df , labels_df, cv=10, verbose=1)
    dummy_scores = cross_val_score(dummy_model, feature_df, labels_df, cv=ShuffleSplit(n_splits=3, train_size=0.7, random_state=0))
    print('randomforest_scores=',np.mean(scores), np.std(scores))
    print('dummy_scores=',np.mean(dummy_scores), np.std(dummy_scores))
    np.random.shuffle(feature_df)
    dummy_model = dummy_model.fit(feature_df[:400,:], labels_df[:400])
    model = model.fit(feature_df[:400,:], labels_df[:400])
    # print(model.predict(feature_df[:100,:]))
    print('randomforest',model.score(feature_df[400:,:], labels_df[400:]))
    print('dummy', dummy_model.score(feature_df[400:,:], labels_df[400:]))
    # return scores, model
    
    ########################
    # MANU ADDED from HERE #
    ########################
    # We set the features we want to use
    # features_to_use = ['var_mgw', 'motif_scores', 'bDNA','compA_d', 'compT_d', 'compG_d', 'compC_d', 'compA_u', 'compT_u', 'compG_u', 'compC_u', 'tfs_D_fw', 'tfs_D_rv', 'tfs_U_fw', 'tfs_U_fw.1', 'intergenetic']
    features_to_use = ['bDNA', 'var_mgw', 'motif_scores','tfs_D_fw', 'tfs_D_rv', 'tfs_U_fw', 'tfs_U_fw.1']
    seqs = ['seq'+str(i) for i in range(21)]
    features_to_use += seqs
    
    # Load features from files in the format requiered for scikit, filtering
    # desired Features
    features, labels, headers = prepare_data_for_classifier(feature_path,labelled_path, randomize = True, only_columns=features_to_use)    

    # DIFFERENT WAYS of running cross-validation! 
    # Running the custom cross-validation just one time, with feature importance
    # analisis
    run_custom_cross(features, labels, headers, single_run=True)
    # We can also run it in verbose mode (will print all the confussion matrixes
    # and scores)
    run_custom_cross(features, labels, headers, single_run=True)
    # Running the custom cross-validation multiple times (using single_run=False)
    # This can be used to calculate average behaviour
    for i in range(10):
        print(run_custom_cross(features, labels, headers, single_run=False))
    

    return None, None
    
def run_custom_cross(features, labels, headers, single_run = True, verbose=False):
    
    ############################
    #   FOREST   customization #
    # --> change from here <-- #
    ############################
    # Number of trees in the forest
    number_of_trees = 300
    # Number of features to train each tree
    max_number_of_features = 'sqrt' # can be 'log'
    # Class Weight
    # If not given, all classes are supposed to have weight one
    #
    # The “balanced” mode uses the values of y to automatically adjust weights
    # inversely proportional to class frequencies in the input data as
    # n_samples / (n_classes * np.bincount(y))
    #
    # The “balanced_subsample” mode is the same as “balanced” except that
    # weights are computed based on the bootstrap sample for every tree grown.
    class_weight = 'balanced'
    ############################
    # -->      to here     <-- #
    ############################ 
    
    ############################
    #   DUMMY    customization #
    # --> change from here <-- #
    ############################
    dummy_strategy = 'stratified'
    ############################
    # -->      to here     <-- #
    ############################     

    ############################
    #  CROSS   customization   #
    # --> change from here <-- #
    ############################  
    number_of_splits = 5
    ############################
    # -->      to here     <-- #
    ############################     
    
    if single_run:
        print("Using features:")
        print(headers)

    # We create TWO estimators
    forest = RandomForestClassifier(n_estimators=number_of_trees, max_features=max_number_of_features, class_weight=class_weight)
    dummy = DummyClassifier(constant=None, random_state=0, strategy=dummy_strategy)
    # We create a crossvalidator
    cross_stratified_kfold = StratifiedKFold(n_splits=number_of_splits, shuffle=True, random_state=None)
    # Some list to store results
    forest_scores_list = []
    dummy_scores_list = []
    forest_cmatrix_list = []
    dummy_cmatrix_list = []
    forest_features_importance_list = []
    forest_features_std_list = []

    # Now we do the actual training and classification
    for train_index, test_index in cross_stratified_kfold.split(features, labels):
        # We define training and test subset, as conducted by the cross-validator
        train_features = features[train_index]
        train_labels = labels[train_index]
        test_features = features[test_index]
        test_labels = labels[test_index]
        # We fit the models
        forest = forest.fit(train_features, train_labels)
        dummy = dummy.fit(train_features,train_labels)
        # We use them to clasify 
        predicted_labels_forest = forest.predict(test_features)
        predicted_labels_dummy = dummy.predict(test_features)
        # We get the MCC scores (1 is perfect classification, 0 is random, -1 is inverse prediction)
        forest_score = matthews_corrcoef(test_labels, predicted_labels_forest, sample_weight=None)
        fpr, tpr, _ = roc_curve(test_labels, predicted_labels_forest)
        # print(roc_auc_score(test_labels, predicted_labels_forest))
        plt.plot(fpr, tpr)
        dummy_score = matthews_corrcoef(test_labels, predicted_labels_dummy, sample_weight=None)
        d_fpr, d_tpr, _ = roc_curve(test_labels, predicted_labels_dummy)
        # plt.plot(fpr, tpr)
        # plt.show()
    
        # We generate the Confusion Matrix 
        # True negatives is C_{0,0}
        # False negatives is C_{1,0}
        # True positives is C_{1,1}
        # False positives is C_{0,1}
        forest_matrix = confusion_matrix(test_labels, predicted_labels_forest, labels=None, sample_weight=None)
        dummy_matrix = confusion_matrix(test_labels, predicted_labels_dummy, labels=None, sample_weight=None)
    
        # We store everything in the appropiate lists
        forest_scores_list.append(forest_score)
        dummy_scores_list.append(dummy_score)
        forest_cmatrix_list.append(forest_matrix)
        dummy_cmatrix_list.append(dummy_matrix)
        forest_features_importance_list.append(forest.feature_importances_)

        forest_feature_std = np.std([tree.feature_importances_ for tree in forest.estimators_],
             axis=0)
        forest_features_std_list.append(forest_feature_std)
        
        if verbose & single_run:
            # We print everything  
            print("Forest score",forest_score)
            print("Dummy score",dummy_score)
            print("\nForest Matrix")
            print(forest_matrix)
            print("\nDummy Matrix")
            print(dummy_matrix)
    
            
    # Now we calculate summurizing scores:
    # best, worst, average and variance of MCC for both classifiers
    forest_score_array = np.array(forest_scores_list)
    forest_max_score = forest_score_array.max()
    forest_min_score = forest_score_array.min()
    forest_avg_score = np.mean(forest_score_array)
    forest_var_score = np.var(forest_score_array)
    
    dummy_score_array = np.array(dummy_scores_list)
    dummy_max_score = dummy_score_array.max()
    dummy_min_score = dummy_score_array.min()
    dummy_avg_score = np.mean(dummy_score_array)
    dummy_var_score = np.var(dummy_score_array)
    
    forest_scores_tuple = (forest_max_score,forest_min_score,forest_avg_score,forest_var_score)
    
    if single_run:
        print('# Scores from cross-validation')
        print(('max','min','average','variance'))
        print('Forest: ')
        print( forest_scores_tuple )
        print('Dummy: ')
        print( (dummy_max_score,dummy_min_score,dummy_avg_score,dummy_var_score) )
            
        # We pick the best run and we extract the importance of features
        bestp_index = np.argmax(forest_score_array)
        bestp_features_imp = forest_features_importance_list[bestp_index]
        bestp_features_std = forest_features_std_list[bestp_index]
        # And we print the Feature Importance (with plot)
        print('The following data is from best performing Forest')
        feature_importance_analysis(bestp_features_imp, bestp_features_std, features, headers, True)
        # And we also print confussion matrix for that forest and that dummy
        print('Best Forest matrix:')
        print(forest_cmatrix_list[bestp_index])
        print(forest_scores_list[bestp_index])
        print('Correspondent Dummy matrix:')
        print(dummy_cmatrix_list[bestp_index])
        print(dummy_scores_list[bestp_index])
    
    return forest_scores_tuple
    
def feature_importance_analysis(importances, std, features_array, features_names, plot=False):
    indices = np.argsort(importances)[::-1]
    # Print the feature ranking
    print("Feature ranking:")

    for f in range(features_array.shape[1]):
        print("%d. feature %s (%f)" % (f + 1, features_names[indices[f]], importances[indices[f]]))

    features_sorted_by_importance = [ features_names[i] for i in indices]
    # Plot the feature importances of the forest
    if plot:
        plt.figure()
        plt.title("Feature importances", fontsize=20)
        plt.bar(range(features_array.shape[1]), importances[indices],
               color="r", yerr=std[indices], align="center")
        plt.xticks(range(features_array.shape[1]), tuple(features_sorted_by_importance), rotation='vertical', fontsize=12)
        plt.ylabel('Feature Importance')
        plt.xlim([-1, features_array.shape[1]])
        # plt.show()

########################
# DEPRECATED FUNCTIONS #
########################
def summurize_cross_score(scores_array):
    warnings.warn('Warning! summurize_cross_score is deprecated')
    best = scores_array.max()
    worst = scores_array.min()
    mean = np.mean(scores_array)
    assert (scores_array < 0).sum > 0, "Danger: we have a negative MCC score. Our way of summurizing MCC scores can not handle this"
    return (best,worst,mean)

def cross_validation(the_feature_df, the_labels_df):
    warnings.warn('Warning! cross_validation is deprecated')  
    # Build a Dummy estimator (classifier)
    dummy_type = 'most_frequent'
#    dummy_type = 'stratified'
    dummy_model = DummyClassifier(constant=None, random_state=0, strategy=dummy_type)
    
    #Build a Random Forest Classifier
    num_trees = 100
    # Number of features: use sqrt, except in case of high-dimensional dataset
    number_of_features = 'sqrt'
#    number_of_features = 'log2'
    forest_model = RandomForestClassifier(n_estimators=num_trees, max_features=number_of_features, class_weight='balanced')
    
    # We create an scorer from the metric "Mathew correlation"
    # The Matthews correlation coefficient (+1 represents a perfect
    #    prediction, 0 an average random prediction and -1 and inverse
    #    prediction).
    #
    # More info https://en.wikipedia.org/wiki/Matthews_correlation_coefficient
    # Sci-kit documentation -> http://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html#sklearn.metrics.matthews_corrcoef
    # Paper that suggest use (according to Wikipedia)
    # http://www.flinders.edu.au/science_engineering/fms/School-CSEM/publications/tech_reps-research_artfcts/TRRA_2007.pdf
    # Didactic explanation of MCC
    # https://lettier.github.io/posts/2016-08-05-matthews-correlation-coefficient.html
    matthews_scorer = make_scorer(matthews_corrcoef, greater_is_better=True, needs_proba=False, needs_threshold=False)

    # We define the cross_validators
    cross_validator_forest = KFold(n_splits=10, shuffle=True, random_state=None)
    cross_validator_dummy = KFold(n_splits=10, shuffle=True, random_state=None)
    # Note: StratifiedKFold could be used also
    #
    # Note: ShuffleSplit could be used, BUT the documentation says:
    #   Note: contrary to other cross-validation strategies, random splits
    #   do not guarantee that all folds will be different, although this is
    #   still very likely for sizeable datasets.
    #
    # Eg: ShuffleSplit(n_splits=10, test_size=0.1, train_size=None, random_state=None)
    #
    # Other cross-validators, check:
    # http://scikit-learn.org/stable/modules/classes.html#module-sklearn.model_selection
    
    # Cross validators will train and test models, returning their score
    score_dummy = cross_val_score(dummy_model, the_feature_df, the_labels_df, cv=cross_validator_dummy, scoring = matthews_scorer)
    score_forest = cross_val_score(forest_model, the_feature_df, the_labels_df, cv=cross_validator_forest, scoring = matthews_scorer)
    
    return (score_forest, score_dummy)
    
def run_cross_validation(feature_path, labelled_path, features_to_use = None):
    warnings.warn('Warning! run_cross_validation is deprecated')  
    # We process the features and labels so as to Scikit like it
    features_array, labels_array, features_names = prepare_data_for_classifier(feature_path, labelled_path, randomize=True, only_columns = features_to_use)
    # We run the cross-validation
    forest_scores , dummy_scores = cross_validation(features_array, labels_array)
    # We return a summury of the MCC scores
    print("\n ## Running CROSS validation ##")
    print(forest_scores)
    return summurize_cross_score(forest_scores)
