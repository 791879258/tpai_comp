from sklearn import linear_model
from sklearn.externals import joblib
import numpy as np
import pandas as pd
import common
import datetime

def read_from_file(file_name, chunk_size=50000):
    reader = pd.read_csv(file_name, iterator=True)
    chunks = []
    mark = True
    while mark:
        try:
            df = reader.get_chunk(chunk_size)
            chunks.append(df)
        except:
            print "Iterator Stop..."
            mark = False
    df = pd.concat(chunks,ignore_index=True)
    return df

def generate_LR_model(file_name):
    train_df = read_from_file(file_name)
    selected_train_df = train_df.filter(regex='label|connectionType_.*|telecomsOperator_.*|sitesetID_.*|positionType_.*|gender_.*|haveBaby_.*|age_scaled')
    train_np = selected_train_df.as_matrix()
    y = train_np[:,0]
    X = train_np[:,1:]
    print 'Train Logistic Regression Model...'
    start_time  = datetime.datetime.now()
    clf = linear_model.LogisticRegression(penalty='l2',C=1.0,solver='sag',n_jobs=-1, tol=1e-6, max_iter=200)#, class_weight='balanced')
    clf.fit(X,y)
    end_time = datetime.datetime.now()
    print 'Training Done..., Time Cost: '
    print (end_time-start_time).seconds

    print 'Save Model...'
    joblib.dump(clf, 'LR.model')
    return clf

def use_model_to_predict(test_file_name, model):
    test_df = read_from_file(test_file_name)
    selected_test_df = test_df.filter(regex='connectionType_.*|telecomsOperator_.*|sitesetID_.*|positionType_.*|gender_.*|haveBaby_.*|age_scaled')
    test_np = selected_test_df.as_matrix()
    print 'Use Model To Predict...'
    model_df =pd.DataFrame({'coef':list(model.coef_.T), 'columns':list(selected_test_df.columns)}) 
    print model_df.describe()
    print model_df.info()
    predicts = model.predict_proba(test_np)
    result = pd.DataFrame({'instanceID':test_df['instanceID'].as_matrix(), 'prob':predicts[:,1].astype(np.float)})
    print predicts, predicts.min(axis=0), predicts.max(axis=0), predicts.sum(axis=1)
    return result

def train_to_predict(train_file_name, test_file_name, out_put):
    LR_clf = generate_LR_model(train_file_name)
    result = use_model_to_predict(test_file_name, LR_clf)
    result.to_csv(out_put, index=False)

def read_model_to_predict(model, test_file_name, out_put):
    clf = joblib.load(model)
    result = use_model_to_predict(test_file_name, clf)
    result.to_csv(out_put, index=False)

if __name__ == '__main__':
    train_to_predict(common.PROCESSED_TRAIN_CSV, common.PROCESSED_TEST_CSV, common.SUBMISSION_CSV)
    #read_model_to_predict('./LR.model', common.PROCESSED_TEST_CSV, 'submission.csv')