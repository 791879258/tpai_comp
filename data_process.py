import numpy as np
import pandas as pd
import common
import matplotlib.pyplot as plt
from sklearn import linear_model
import sklearn.preprocessing as preprocessing

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

def process_ad_file(src_file_name,dst_file_name):
    origin_ad_df = read_from_file(src_file_name)
    origin_ad_df['appCategoryLevel1ID'] = origin_ad_df['appCategory'].as_matrix() / 100
    origin_ad_df['appCategoryLevel2ID'] = origin_ad_df['appCategory'] % 100
    #print origin_ad_df.info()
    #print origin_ad_df.describe()
    dummy_app_platform = pd.get_dummies(origin_ad_df['appPlatform'], prefix='appPlatform')
    processd_ad_df = pd.concat([origin_ad_df,dummy_app_platform],axis=1)
    
    processd_ad_df.to_csv(dst_file_name, index=False)

def process_position_file(src_file_name,dst_file_name):
    origin_pos_df = read_from_file(src_file_name)
    #print origin_pos_df.info()
    #print origin_pos_df.describe()
    dummy_siteset = pd.get_dummies(origin_pos_df['sitesetID'], prefix='sitesetID')
    dummy_pos_type = pd.get_dummies(origin_pos_df['positionType'], prefix='positionType')
    processd_pos_df = pd.concat([origin_pos_df,dummy_siteset,dummy_pos_type], axis=1)

    processd_pos_df.to_csv(dst_file_name, index=False)

def process_user_file(src_file_name,dst_file_name):
    origin_user_df = read_from_file(src_file_name)
    origin_user_df['hometownProvID'] = origin_user_df['hometown'].as_matrix() / 100
    origin_user_df['hometownProvID'] = origin_user_df['hometown'] % 100
    origin_user_df['residenceProvID'] = origin_user_df['residence'].as_matrix() / 100
    origin_user_df['residenceCityID'] = origin_user_df['residence'] % 100
    #print origin_user_df.info()
    #print origin_user_df.describe()
    dummy_gender = pd.get_dummies(origin_user_df['gender'], prefix='gender')
    dummy_education = pd.get_dummies(origin_user_df['education'], prefix='education')
    dummy_marr_status = pd.get_dummies(origin_user_df['marriageStatus'], prefix='marriageStatus')
    dummy_have_baby = pd.get_dummies(origin_user_df['haveBaby'], prefix='haveBaby')
    processd_user_df = pd.concat([origin_user_df, dummy_gender, dummy_education, dummy_marr_status, dummy_have_baby], axis=1)

    processd_user_df.to_csv(dst_file_name, index=False)

#Old Methods
def process_train_file(src_file_name, dst_file_name, is_skip_regenerate=False):
    ori_train_df = read_from_file(src_file_name)
    dummy_connect_type = pd.get_dummies(ori_train_df['connectionType'], prefix='connectionType')
    dummy_telecoms = pd.get_dummies(ori_train_df['telecomsOperator'], prefix='telecomsOperator')
    ori_train_df = pd.concat([ori_train_df, dummy_connect_type, dummy_telecoms], axis=1)
    
    if not is_skip_regenerate:
        print "Process Ad File..."
        process_ad_file(common.ORIGIN_AD_CSV,common.PROCESSED_AD_CSV)
        print "Process Position File..."
        process_position_file(common.ORIGIN_POSITION_CSV, common.PROCESSED_POSITION_CSV)
        print "Process User File..."
        process_user_file(common.ORIGIN_USER_CSV, common.PROCESSED_USER_CSV)
    
    #merge data frame
    print "Merge Data..."
    processed_ad_df = read_from_file(common.PROCESSED_AD_CSV)
    processed_pos_df = read_from_file(common.PROCESSED_POSITION_CSV)
    processed_user_df = read_from_file(common.PROCESSED_USER_CSV)
    merge_train_data = pd.merge(ori_train_df,processed_ad_df,how='left',on='creativeID')
    merge_train_data = pd.merge(merge_train_data, processed_pos_df,how='left', on='positionID')
    merge_train_data = pd.merge(merge_train_data, processed_user_df,how='left', on='userID')
    scaler = preprocessing.StandardScaler()
    age_scale_param = scaler.fit(merge_train_data['age'])
    merge_train_data['age_scaled'] = scaler.fit_transform(merge_train_data['age'], age_scale_param)

    merge_train_data.to_csv(dst_file_name,index=False)
    return age_scale_param

def process_test_file(src_file_name, dst_file_name, scaler_para, is_skip_regenerate=False):
    ori_test_df = read_from_file(src_file_name)
    dummy_connect_type = pd.get_dummies(ori_test_df['connectionType'], prefix='connectionType')
    dummy_telecoms = pd.get_dummies(ori_test_df['telecomsOperator'], prefix='telecomsOperator')
    ori_test_df = pd.concat([ori_test_df, dummy_connect_type, dummy_telecoms], axis=1)
    
    if not is_skip_regenerate:
        print "Process Ad File..."
        process_ad_file(common.ORIGIN_AD_CSV,common.PROCESSED_AD_CSV)
        print "Process Position File..."
        process_position_file(common.ORIGIN_POSITION_CSV, common.PROCESSED_POSITION_CSV)
        print "Process User File..."
        process_user_file(common.ORIGIN_USER_CSV, common.PROCESSED_USER_CSV)
    
    #merge data frame
    print "Merge Data..."
    processed_ad_df = read_from_file(common.PROCESSED_AD_CSV)
    processed_pos_df = read_from_file(common.PROCESSED_POSITION_CSV)
    processed_user_df = read_from_file(common.PROCESSED_USER_CSV)
    merge_test_data = pd.merge(ori_test_df,processed_ad_df,how='left',on='creativeID')
    merge_test_data = pd.merge(merge_test_data, processed_pos_df,how='left', on='positionID')
    merge_test_data = pd.merge(merge_test_data, processed_user_df,how='left', on='userID')
    scaler = preprocessing.StandardScaler()
    merge_test_data['age_scaled'] = scaler.fit_transform(merge_test_data['age'], scaler_para)

    merge_test_data.to_csv(dst_file_name,index=False)

if __name__ == '__main__':
    process_ad_file(common.ORIGIN_AD_CSV, common.PROCESSED_AD_CSV)
    process_position_file(common.ORIGIN_POSITION_CSV, common.PROCESSED_POSITION_CSV)
    process_user_file(common.ORIGIN_USER_CSV, common.PROCESSED_USER_CSV)
    #scaler_para = process_train_file(common.ORIGIN_TRAIN_CSV, common.PROCESSED_TRAIN_CSV,False)
    #process_test_file(common.ORIGIN_TEST_CSV, common.PROCESSED_TEST_CSV, scaler_para, True)