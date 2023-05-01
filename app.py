from flask import Flask, send_from_directory
from flask_cors import CORS, cross_origin
import json
import pandas as pd
import pickle
import datetime
# from Recommendations import Recommendations
from Business import Business
from AE_CF import AE_CF
import bz2file as bz2
# print("pickle version"+pickle.format_version)

# Building Ratings Matrix
from scipy.sparse import coo_matrix
import numpy as np
from collections import defaultdict
from Business import Business

app = Flask(__name__, static_folder='./build', static_url_path="")
CORS(app)

business_df = pd.DataFrame()
reviews_df = pd.DataFrame()
# create an empty dictionary to store the dataframes
hotel_state_df_map = {}
restaurent_state_df_map = {}
nightlife_state_df_map = {}

hotel_state_rec_map = {}

restaurent_state_rec_map = {}

nightlife_state_rec_map = {}

hotel_mf_map = {}

restaurent_mf_map = {}

nightlife_mf_map = {}

hotel_aecf_map = {}

restaurent_aecf_map = {}

nightlife_aecf_map = {}

PA_Hotel_Recommendation = None
FL_Hotel_Recommendation = None
TN_Hotel_Recommendation = None
IN_Hotel_Recommendation = None
MO_Hotel_Recommendation = None
LA_Hotel_Recommendation = None
AZ_Hotel_Recommendation = None
NJ_Hotel_Recommendation = None
NV_Hotel_Recommendation = None
AB_Hotel_Recommendation = None

PA_Restaurent_Recommendation = None
FL_Restaurent_Recommendation = None
TN_Restaurent_Recommendation = None
IN_Restaurent_Recommendation = None
MO_Restaurent_Recommendation = None
LA_Restaurent_Recommendation = None
AZ_Restaurent_Recommendation = None
NJ_Restaurent_Recommendation = None
NV_Restaurent_Recommendation = None
AB_Restaurent_Recommendation = None


PA_Nightlife_Recommendation = None
FL_Nightlife_Recommendation = None
TN_Nightlife_Recommendation = None
IN_Nightlife_Recommendation = None
MO_Nightlife_Recommendation = None
LA_Nightlife_Recommendation = None
AZ_Nightlife_Recommendation = None
NJ_Nightlife_Recommendation = None
NV_Nightlife_Recommendation = None
AB_Nightlife_Recommendation = None

PA_Hotel_MF = None
FL_Hotel_MF = None
TN_Hotel_MF = None
IN_Hotel_MF = None
MO_Hotel_MF = None
LA_Hotel_MF = None
AZ_Hotel_MF = None
NJ_Hotel_MF = None
NV_Hotel_MF = None
AB_Hotel_MF = None

PA_Restaurent_MF = None
FL_Restaurent_MF = None
TN_Restaurent_MF = None
IN_Restaurent_MF = None
MO_Restaurent_MF = None
LA_Restaurent_MF = None
AZ_Restaurent_MF = None
NJ_Restaurent_MF = None
NV_Restaurent_MF = None
AB_Restaurent_MF = None

PA_Nightlife_MF = None
FL_Nightlife_MF = None
TN_Nightlife_MF = None
IN_Nightlife_MF = None
MO_Nightlife_MF = None
LA_Nightlife_MF = None
AZ_Nightlife_MF = None
NJ_Nightlife_MF = None
NV_Nightlife_MF = None
AB_Nightlife_MF = None

PA_Hotel_AECF = None
FL_Hotel_AECF = None
TN_Hotel_AECF = None
IN_Hotel_AECF = None
MO_Hotel_AECF = None
LA_Hotel_AECF = None
AZ_Hotel_AECF = None
NJ_Hotel_AECF = None
NV_Hotel_AECF = None
AB_Hotel_AECF = None

PA_Restaurent_AECF = None
FL_Restaurent_AECF = None
TN_Restaurent_AECF = None
IN_Restaurent_AECF = None
MO_Restaurent_AECF = None
LA_Restaurent_AECF = None
AZ_Restaurent_AECF = None
NJ_Restaurent_AECF = None
NV_Restaurent_AECF = None
AB_Restaurent_AECF = None

PA_Nightlife_AECF = None
FL_Nightlife_AECF = None
TN_Nightlife_AECF = None
IN_Nightlife_AECF = None
MO_Nightlife_AECF = None
LA_Nightlife_AECF = None
AZ_Nightlife_AECF = None
NJ_Nightlife_AECF = None
NV_Nightlife_AECF = None
AB_Nightlife_AECF = None


@app.route('/profile')
@cross_origin()
def my_profile():
    response_body = {
        "name": "Nagato",
        "about": "Hello! I'm a full stack developer that loves python and javascript"
    }
    return response_body


@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')


def loadCSV():
    print("Loading CSV Files...")
    print(datetime.datetime.now())
    global reviews_df
    reviews_df = pd.read_csv('yelp_academic_dataset_review.csv')
    # user_df = pd.read_csv('yelp_academic_dataset_user.csv')
    global business_df
    business_df = pd.read_csv('yelp_academic_dataset_business.csv')
    business_df = business_df.dropna(subset=['categories'])
    print("Loading CSV Files Completed...")
    print(datetime.datetime.now())
    print("\n")


def getTopStates():
    # Get Top Ten States
    print("Generating Top 10 States Dataframes...")
    unique_states = business_df['state'].unique()
    state_map = dict()
    for s in unique_states:
        state_map[s] = business_df[business_df['state'] == s].shape[0]
    # 'CA' 'MO' 'AZ' 'PA' 'TN' 'FL' 'IN' 'LA' 'AB' 'NV' 'ID' 'DE' 'IL' 'NJ' 'NC' 'CO' 'WA' 'HI' 'UT' 'TX' 'MT' 'MI' 'SD' 'XMS' 'MA' 'VI' 'VT'
    top_states = [state[0] for state in sorted(sorted(state_map.items(
    ), key=lambda x: x[1], reverse=True), key=lambda x: x[1], reverse=True)[:10]]
    print(top_states)

    # Creating mask for Hotels & Travel
    hotel_mask = business_df['categories'].str.contains('Hotels & Travel')
    hotel_df = business_df[hotel_mask]

    # Creating mask for Restaurents
    restaurent_mask = business_df['categories'].str.contains('Restaurants')
    restaurent_df = business_df[restaurent_mask]

    # Creating mask for Nightlife
    nightlife_mask = business_df['categories'].str.contains('Nightlife')
    nightlife_df = business_df[nightlife_mask]

    global hotel_state_df_map
    global restaurent_state_df_map
    global nightlife_state_df_map

    for state in top_states:
        df_name = f'business_df_{state}'

        hotel_state_df = hotel_df[hotel_df['state'] == state]
        restaurent_state_df = restaurent_df[restaurent_df['state'] == state]
        nightlife_state_df = nightlife_df[nightlife_df['state'] == state]

        exec(f"{df_name} = hotel_state_df")
        # add the dataframe to the dictionary with the state abbreviation as the key
        hotel_state_df_map[state] = hotel_state_df

        exec(f"{df_name} = restaurent_state_df")
        # add the dataframe to the dictionary with the state abbreviation as the key
        restaurent_state_df_map[state] = restaurent_state_df

        exec(f"{df_name} = nightlife_state_df")
        # add the dataframe to the dictionary with the state abbreviation as the key
        nightlife_state_df_map[state] = nightlife_state_df


def compressed_pickle(title, data):
    with bz2.BZ2File(title + ".pbz2", "w") as f:
        pickle.dump(data, f)


def decompress_pickle(file):
    data = bz2.BZ2File(file, "rb")
    data = pickle.load(data)
    return data


def helper_fun():
    global hotel_state_rec_map

    global restaurent_state_rec_map

    global nightlife_state_rec_map

    global hotel_mf_map

    global restaurent_mf_map

    global nightlife_mf_map

    global hotel_aecf_map

    global restaurent_aecf_map

    global nightlife_aecf_map

    print("Loading Hotel Data Files...")
    print(datetime.datetime.now())
    PA_Hotel_Recommendation = decompress_pickle(
        "data/hotel/PA_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['PA'] = PA_Hotel_Recommendation
    FL_Hotel_Recommendation = decompress_pickle(
        "data/hotel/FL_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['FL'] = FL_Hotel_Recommendation
    TN_Hotel_Recommendation = decompress_pickle(
        "data/hotel/TN_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['TN'] = TN_Hotel_Recommendation
    IN_Hotel_Recommendation = decompress_pickle(
        "data/hotel/IN_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['IN'] = IN_Hotel_Recommendation
    MO_Hotel_Recommendation = decompress_pickle(
        "data/hotel/MO_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['MO'] = MO_Hotel_Recommendation
    LA_Hotel_Recommendation = decompress_pickle(
        "data/hotel/LA_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['LA'] = LA_Hotel_Recommendation
    AZ_Hotel_Recommendation = decompress_pickle(
        "data/hotel/AZ_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['AZ'] = AZ_Hotel_Recommendation
    NJ_Hotel_Recommendation = decompress_pickle(
        "data/hotel/NJ_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['NJ'] = NJ_Hotel_Recommendation
    NV_Hotel_Recommendation = decompress_pickle(
        "data/hotel/NV_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['NV'] = NV_Hotel_Recommendation
    AB_Hotel_Recommendation = decompress_pickle(
        "data/hotel/AB_Hotel_Recommendation.pbz2")
    hotel_state_rec_map['AB'] = AB_Hotel_Recommendation
    print("Loading Hotel Data Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Restaurent Data Files...")
    print(datetime.datetime.now())
    PA_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/PA_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['PA'] = PA_Restaurent_Recommendation
    FL_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/FL_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['FL'] = FL_Restaurent_Recommendation
    TN_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/TN_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['TN'] = TN_Restaurent_Recommendation
    IN_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/IN_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['IN'] = IN_Restaurent_Recommendation
    MO_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/MO_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['MO'] = MO_Restaurent_Recommendation
    LA_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/LA_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['LA'] = LA_Restaurent_Recommendation
    AZ_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/AZ_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['AZ'] = AZ_Restaurent_Recommendation
    NJ_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/NJ_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['NJ'] = NJ_Restaurent_Recommendation
    NV_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/NV_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['NV'] = NV_Restaurent_Recommendation
    AB_Restaurent_Recommendation = decompress_pickle(
        "data/restaurent/AB_Restaurent_Recommendation.pbz2")
    restaurent_state_rec_map['AB'] = AB_Restaurent_Recommendation
    print("Loading Restaurent Data Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Nightlife Data Files...")
    print(datetime.datetime.now())
    PA_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/PA_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['PA'] = PA_Nightlife_Recommendation
    FL_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/FL_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['FL'] = FL_Nightlife_Recommendation
    TN_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/TN_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['TN'] = TN_Nightlife_Recommendation
    IN_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/IN_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['IN'] = IN_Nightlife_Recommendation
    MO_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/MO_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['MO'] = MO_Nightlife_Recommendation
    LA_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/LA_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['LA'] = LA_Nightlife_Recommendation
    AZ_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/AZ_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['AZ'] = AZ_Nightlife_Recommendation
    NJ_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/NJ_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['NJ'] = NJ_Nightlife_Recommendation
    NV_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/NV_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['NV'] = NV_Nightlife_Recommendation
    AB_Nightlife_Recommendation = decompress_pickle(
        "data/nightlife/AB_Nightlife_Recommendation.pbz2")
    nightlife_state_rec_map['AB'] = AB_Nightlife_Recommendation
    print("Loading Nightlife Data Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Hotel MF Files...")
    print(datetime.datetime.now())
    PA_Hotel_MF = decompress_pickle("data/hotel/PA_Hotel_MF.pbz2")
    hotel_mf_map['PA'] = PA_Hotel_MF
    FL_Hotel_MF = decompress_pickle("data/hotel/FL_Hotel_MF.pbz2")
    hotel_mf_map['FL'] = FL_Hotel_MF
    TN_Hotel_MF = decompress_pickle("data/hotel/TN_Hotel_MF.pbz2")
    hotel_mf_map['TN'] = TN_Hotel_MF
    IN_Hotel_MF = decompress_pickle("data/hotel/IN_Hotel_MF.pbz2")
    hotel_mf_map['IN'] = IN_Hotel_MF
    MO_Hotel_MF = decompress_pickle("data/hotel/MO_Hotel_MF.pbz2")
    hotel_mf_map['MO'] = MO_Hotel_MF
    LA_Hotel_MF = decompress_pickle("data/hotel/LA_Hotel_MF.pbz2")
    hotel_mf_map['LA'] = LA_Hotel_MF
    AZ_Hotel_MF = decompress_pickle("data/hotel/AZ_Hotel_MF.pbz2")
    hotel_mf_map['AZ'] = AZ_Hotel_MF
    NJ_Hotel_MF = decompress_pickle("data/hotel/NJ_Hotel_MF.pbz2")
    hotel_mf_map['NJ'] = NJ_Hotel_MF
    NV_Hotel_MF = decompress_pickle("data/hotel/NV_Hotel_MF.pbz2")
    hotel_mf_map['NV'] = NV_Hotel_MF
    AB_Hotel_MF = decompress_pickle("data/hotel/AB_Hotel_MF.pbz2")
    hotel_mf_map['AB'] = AB_Hotel_MF
    print("Loading Hotel MF Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Restaurent MF Files...")
    print(datetime.datetime.now())
    PA_Restaurent_MF = decompress_pickle(
        "data/restaurent/PA_Restaurent_MF.pbz2")
    restaurent_mf_map['PA'] = PA_Restaurent_MF
    FL_Restaurent_MF = decompress_pickle(
        "data/restaurent/FL_Restaurent_MF.pbz2")
    restaurent_mf_map['FL'] = FL_Restaurent_MF
    TN_Restaurent_MF = decompress_pickle(
        "data/restaurent/TN_Restaurent_MF.pbz2")
    restaurent_mf_map['TN'] = TN_Restaurent_MF
    IN_Restaurent_MF = decompress_pickle(
        "data/restaurent/IN_Restaurent_MF.pbz2")
    restaurent_mf_map['IN'] = IN_Restaurent_MF
    MO_Restaurent_MF = decompress_pickle(
        "data/restaurent/MO_Restaurent_MF.pbz2")
    restaurent_mf_map['MO'] = MO_Restaurent_MF
    LA_Restaurent_MF = decompress_pickle(
        "data/restaurent/LA_Restaurent_MF.pbz2")
    restaurent_mf_map['LA'] = LA_Restaurent_MF
    AZ_Restaurent_MF = decompress_pickle(
        "data/restaurent/AZ_Restaurent_MF.pbz2")
    restaurent_mf_map['AZ'] = AZ_Restaurent_MF
    NJ_Restaurent_MF = decompress_pickle(
        "data/restaurent/NJ_Restaurent_MF.pbz2")
    restaurent_mf_map['NJ'] = NJ_Restaurent_MF
    NV_Restaurent_MF = decompress_pickle(
        "data/restaurent/NV_Restaurent_MF.pbz2")
    restaurent_mf_map['NV'] = NV_Restaurent_MF
    AB_Restaurent_MF = decompress_pickle(
        "data/restaurent/AB_Restaurent_MF.pbz2")
    restaurent_mf_map['AB'] = AB_Restaurent_MF
    print("Loading Restaurent MF Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Nightlife MF Files...")
    print(datetime.datetime.now())
    PA_Nightlife_MF = decompress_pickle(
        "data/nightlife/PA_Nightlife_MF.pbz2")
    nightlife_mf_map['PA'] = PA_Nightlife_MF
    FL_Nightlife_MF = decompress_pickle(
        "data/nightlife/FL_Nightlife_MF.pbz2")
    nightlife_mf_map['FL'] = FL_Nightlife_MF
    TN_Nightlife_MF = decompress_pickle(
        "data/nightlife/TN_Nightlife_MF.pbz2")
    nightlife_mf_map['TN'] = TN_Nightlife_MF
    IN_Nightlife_MF = decompress_pickle(
        "data/nightlife/IN_Nightlife_MF.pbz2")
    nightlife_mf_map['IN'] = IN_Nightlife_MF
    MO_Nightlife_MF = decompress_pickle(
        "data/nightlife/MO_Nightlife_MF.pbz2")
    nightlife_mf_map['MO'] = MO_Nightlife_MF
    LA_Nightlife_MF = decompress_pickle(
        "data/nightlife/LA_Nightlife_MF.pbz2")
    nightlife_mf_map['LA'] = LA_Nightlife_MF
    AZ_Nightlife_MF = decompress_pickle(
        "data/nightlife/AZ_Nightlife_MF.pbz2")
    nightlife_mf_map['AZ'] = AZ_Nightlife_MF
    NJ_Nightlife_MF = decompress_pickle(
        "data/nightlife/NJ_Nightlife_MF.pbz2")
    nightlife_mf_map['NJ'] = NJ_Nightlife_MF
    NV_Nightlife_MF = decompress_pickle(
        "data/nightlife/NV_Nightlife_MF.pbz2")
    nightlife_mf_map['NV'] = NV_Nightlife_MF
    AB_Nightlife_MF = decompress_pickle(
        "data/nightlife/AB_Nightlife_MF.pbz2")
    nightlife_mf_map['AB'] = AB_Nightlife_MF
    print("Loading Nightlife MF Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Hotel AECF Files...")
    print(datetime.datetime.now())
    PA_Hotel_AECF = decompress_pickle(
        "data/hotel/PA_Hotel_AECF.pbz2")
    hotel_aecf_map['PA'] = PA_Hotel_AECF
    FL_Hotel_AECF = decompress_pickle(
        "data/hotel/FL_Hotel_AECF.pbz2")
    hotel_aecf_map['FL'] = FL_Hotel_AECF
    TN_Hotel_AECF = decompress_pickle(
        "data/hotel/TN_Hotel_AECF.pbz2")
    hotel_aecf_map['TN'] = TN_Hotel_AECF
    IN_Hotel_AECF = decompress_pickle(
        "data/hotel/IN_Hotel_AECF.pbz2")
    hotel_aecf_map['IN'] = IN_Hotel_AECF
    MO_Hotel_AECF = decompress_pickle(
        "data/hotel/MO_Hotel_AECF.pbz2")
    hotel_aecf_map['MO'] = MO_Hotel_AECF
    LA_Hotel_AECF = decompress_pickle(
        "data/hotel/LA_Hotel_AECF.pbz2")
    hotel_aecf_map['LA'] = LA_Hotel_AECF
    AZ_Hotel_AECF = decompress_pickle(
        "data/hotel/AZ_Hotel_AECF.pbz2")
    hotel_aecf_map['AZ'] = AZ_Hotel_AECF
    NJ_Hotel_AECF = decompress_pickle(
        "data/hotel/NJ_Hotel_AECF.pbz2")
    hotel_aecf_map['NJ'] = NJ_Hotel_AECF
    NV_Hotel_AECF = decompress_pickle(
        "data/hotel/NV_Hotel_AECF.pbz2")
    hotel_aecf_map['NV'] = NV_Hotel_AECF
    AB_Hotel_AECF = decompress_pickle(
        "data/hotel/AB_Hotel_AECF.pbz2")
    hotel_aecf_map['AB'] = AB_Hotel_AECF
    print("Loading Hotel AECF Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Restaurent AECF Files...")
    print(datetime.datetime.now())
    PA_Restaurent_AECF = decompress_pickle(
        "data/restaurent/PA_Restaurent_AECF.pbz2")
    restaurent_aecf_map['PA'] = PA_Restaurent_AECF
    FL_Restaurent_AECF = decompress_pickle(
        "data/restaurent/FL_Restaurent_AECF.pbz2")
    restaurent_aecf_map['FL'] = FL_Restaurent_AECF
    TN_Restaurent_AECF = decompress_pickle(
        "data/restaurent/TN_Restaurent_AECF.pbz2")
    restaurent_aecf_map['TN'] = TN_Restaurent_AECF
    IN_Restaurent_AECF = decompress_pickle(
        "data/restaurent/IN_Restaurent_AECF.pbz2")
    restaurent_aecf_map['IN'] = IN_Restaurent_AECF
    MO_Restaurent_AECF = decompress_pickle(
        "data/restaurent/MO_Restaurent_AECF.pbz2")
    restaurent_aecf_map['MO'] = MO_Restaurent_AECF
    LA_Restaurent_AECF = decompress_pickle(
        "data/restaurent/LA_Restaurent_AECF.pbz2")
    restaurent_aecf_map['LA'] = LA_Restaurent_AECF
    AZ_Restaurent_AECF = decompress_pickle(
        "data/restaurent/AZ_Restaurent_AECF.pbz2")
    restaurent_aecf_map['AZ'] = AZ_Restaurent_AECF
    NJ_Restaurent_AECF = decompress_pickle(
        "data/restaurent/NJ_Restaurent_AECF.pbz2")
    restaurent_aecf_map['NJ'] = NJ_Restaurent_AECF
    NV_Restaurent_AECF = decompress_pickle(
        "data/restaurent/NV_Restaurent_AECF.pbz2")
    restaurent_aecf_map['NV'] = NV_Restaurent_AECF
    AB_Restaurent_AECF = decompress_pickle(
        "data/restaurent/AB_Restaurent_AECF.pbz2")
    restaurent_aecf_map['AB'] = AB_Restaurent_AECF
    print("Loading Restaurent AECF Files Completed...")
    print(datetime.datetime.now())
    print("\n")

    print("Loading Nightlife AECF Files...")
    print(datetime.datetime.now())
    PA_Nightlife_AECF = decompress_pickle(
        "data/nightlife/PA_Nightlife_AECF.pbz2")
    nightlife_aecf_map['PA'] = PA_Nightlife_AECF
    FL_Nightlife_AECF = decompress_pickle(
        "data/nightlife/FL_Nightlife_AECF.pbz2")
    nightlife_aecf_map['FL'] = FL_Nightlife_AECF
    TN_Nightlife_AECF = decompress_pickle(
        "data/nightlife/TN_Nightlife_AECF.pbz2")
    nightlife_aecf_map['TN'] = TN_Nightlife_AECF
    IN_Nightlife_AECF = decompress_pickle(
        "data/nightlife/IN_Nightlife_AECF.pbz2")
    nightlife_aecf_map['IN'] = IN_Nightlife_AECF
    MO_Nightlife_AECF = decompress_pickle(
        "data/nightlife/MO_Nightlife_AECF.pbz2")
    nightlife_aecf_map['MO'] = MO_Nightlife_AECF
    LA_Nightlife_AECF = decompress_pickle(
        "data/nightlife/LA_Nightlife_AECF.pbz2")
    nightlife_aecf_map['LA'] = LA_Nightlife_AECF
    AZ_Nightlife_AECF = decompress_pickle(
        "data/nightlife/AZ_Nightlife_AECF.pbz2")
    nightlife_aecf_map['AZ'] = AZ_Nightlife_AECF
    NJ_Nightlife_AECF = decompress_pickle(
        "data/nightlife/NJ_Nightlife_AECF.pbz2")
    nightlife_aecf_map['NJ'] = NJ_Nightlife_AECF
    NV_Nightlife_AECF = decompress_pickle(
        "data/nightlife/NV_Nightlife_AECF.pbz2")
    nightlife_aecf_map['NV'] = NV_Nightlife_AECF
    AB_Nightlife_AECF = decompress_pickle(
        "data/nightlife/AB_Nightlife_AECF.pbz2")
    nightlife_aecf_map['AB'] = AB_Nightlife_AECF
    print("Loading Nightlife AECF Files Completed...")
    print(datetime.datetime.now())
    print("\n")


# with app.app_context():
#     helper_fun()

# loadCSV()
# getTopStates()
# hotel_state_rec_map = {}

# restaurent_state_rec_map = {}

# nightlife_state_rec_map = {}

# hotel_mf_map = {}

# restaurent_mf_map = {}

# nightlife_mf_map = {}

# hotel_aecf_map = {}

# restaurent_aecf_map = {}

# nightlife_aecf_map = {}

# Write APIs here
# def completeMaps():
#     global hotel_state_rec_map
#     global restaurent_state_rec_map
#     global nightlife_state_rec_map
#     global hotel_mf_map
#     global restaurent_mf_map
#     global nightlife_mf_map
#     global hotel_aecf_map
#     global restaurent_aecf_map
#     global nightlife_aecf_map

#     global PA_Hotel_Recommendation
#     global FL_Hotel_Recommendation
#     global TN_Hotel_Recommendation
#     global IN_Hotel_Recommendation
#     global MO_Hotel_Recommendation
#     global LA_Hotel_Recommendation
#     global AZ_Hotel_Recommendation
#     global NJ_Hotel_Recommendation
#     global NV_Hotel_Recommendation
#     global AB_Hotel_Recommendation

#     global PA_Restaurent_Recommendation
#     global FL_Restaurent_Recommendation
#     global TN_Restaurent_Recommendation
#     global IN_Restaurent_Recommendation
#     global MO_Restaurent_Recommendation
#     global LA_Restaurent_Recommendation
#     global AZ_Restaurent_Recommendation
#     global NJ_Restaurent_Recommendation
#     global NV_Restaurent_Recommendation
#     global AB_Restaurent_Recommendation

#     global PA_Nightlife_Recommendation
#     global FL_Nightlife_Recommendation
#     global TN_Nightlife_Recommendation
#     global IN_Nightlife_Recommendation
#     global MO_Nightlife_Recommendation
#     global LA_Nightlife_Recommendation
#     global AZ_Nightlife_Recommendation
#     global NJ_Nightlife_Recommendation
#     global NV_Nightlife_Recommendation
#     global AB_Nightlife_Recommendation

#     global PA_Hotel_MF
#     global FL_Hotel_MF
#     global TN_Hotel_MF
#     global IN_Hotel_MF
#     global MO_Hotel_MF
#     global LA_Hotel_MF
#     global AZ_Hotel_MF
#     global NJ_Hotel_MF
#     global NV_Hotel_MF
#     global AB_Hotel_MF

#     global PA_Restaurent_MF
#     global FL_Restaurent_MF
#     global TN_Restaurent_MF
#     global IN_Restaurent_MF
#     global MO_Restaurent_MF
#     global LA_Restaurent_MF
#     global AZ_Restaurent_MF
#     global NJ_Restaurent_MF
#     global NV_Restaurent_MF
#     global AB_Restaurent_MF

#     global PA_Nightlife_MF
#     global FL_Nightlife_MF
#     global TN_Nightlife_MF
#     global IN_Nightlife_MF
#     global MO_Nightlife_MF
#     global LA_Nightlife_MF
#     global AZ_Nightlife_MF
#     global NJ_Nightlife_MF
#     global NV_Nightlife_MF
#     global AB_Nightlife_MF

#     global PA_Hotel_AECF
#     global FL_Hotel_AECF
#     global TN_Hotel_AECF
#     global IN_Hotel_AECF
#     global MO_Hotel_AECF
#     global LA_Hotel_AECF
#     global AZ_Hotel_AECF
#     global NJ_Hotel_AECF
#     global NV_Hotel_AECF
#     global AB_Hotel_AECF

#     global PA_Restaurent_AECF
#     global FL_Restaurent_AECF
#     global TN_Restaurent_AECF
#     global IN_Restaurent_AECF
#     global MO_Restaurent_AECF
#     global LA_Restaurent_AECF
#     global AZ_Restaurent_AECF
#     global NJ_Restaurent_AECF
#     global NV_Restaurent_AECF
#     global AB_Restaurent_AECF

#     global PA_Nightlife_AECF
#     global FL_Nightlife_AECF
#     global TN_Nightlife_AECF
#     global IN_Nightlife_AECF
#     global MO_Nightlife_AECF
#     global LA_Nightlife_AECF
#     global AZ_Nightlife_AECF
#     global NJ_Nightlife_AECF
#     global NV_Nightlife_AECF
#     global AB_Nightlife_AECF

#     hotel_state_rec_map['PA'] = PA_Hotel_Recommendation
#     hotel_state_rec_map['FL'] = FL_Hotel_Recommendation
#     hotel_state_rec_map['TN'] = TN_Hotel_Recommendation
#     hotel_state_rec_map['IN'] = IN_Hotel_Recommendation
#     hotel_state_rec_map['MO'] = MO_Hotel_Recommendation
#     hotel_state_rec_map['LA'] = LA_Hotel_Recommendation
#     hotel_state_rec_map['AZ'] = AZ_Hotel_Recommendation
#     hotel_state_rec_map['NJ'] = NJ_Hotel_Recommendation
#     hotel_state_rec_map['NV'] = NV_Hotel_Recommendation
#     hotel_state_rec_map['AB'] = AB_Hotel_Recommendation

#     restaurent_state_rec_map['PA'] = PA_Restaurent_Recommendation
#     restaurent_state_rec_map['FL'] = FL_Restaurent_Recommendation
#     restaurent_state_rec_map['TN'] = TN_Restaurent_Recommendation
#     restaurent_state_rec_map['IN'] = IN_Restaurent_Recommendation
#     restaurent_state_rec_map['MO'] = MO_Restaurent_Recommendation
#     restaurent_state_rec_map['LA'] = LA_Restaurent_Recommendation
#     restaurent_state_rec_map['AZ'] = AZ_Restaurent_Recommendation
#     restaurent_state_rec_map['NJ'] = NJ_Restaurent_Recommendation
#     restaurent_state_rec_map['NV'] = NV_Restaurent_Recommendation
#     restaurent_state_rec_map['AB'] = AB_Restaurent_Recommendation

#     nightlife_state_rec_map['PA'] = PA_Nightlife_Recommendation
#     nightlife_state_rec_map['FL'] = FL_Nightlife_Recommendation
#     nightlife_state_rec_map['TN'] = TN_Nightlife_Recommendation
#     nightlife_state_rec_map['IN'] = IN_Nightlife_Recommendation
#     nightlife_state_rec_map['MO'] = MO_Nightlife_Recommendation
#     nightlife_state_rec_map['LA'] = LA_Nightlife_Recommendation
#     nightlife_state_rec_map['AZ'] = AZ_Nightlife_Recommendation
#     nightlife_state_rec_map['NJ'] = NJ_Nightlife_Recommendation
#     nightlife_state_rec_map['NV'] = NV_Nightlife_Recommendation
#     nightlife_state_rec_map['AB'] = AB_Nightlife_Recommendation

#     hotel_mf_map['PA'] = PA_Hotel_MF
#     hotel_mf_map['FL'] = FL_Hotel_MF
#     hotel_mf_map['TN'] = TN_Hotel_MF
#     hotel_mf_map['IN'] = IN_Hotel_MF
#     hotel_mf_map['MO'] = MO_Hotel_MF
#     hotel_mf_map['LA'] = LA_Hotel_MF
#     hotel_mf_map['AZ'] = AZ_Hotel_MF
#     hotel_mf_map['NJ'] = NJ_Hotel_MF
#     hotel_mf_map['NV'] = NV_Hotel_MF
#     hotel_mf_map['AB'] = AB_Hotel_MF

#     restaurent_mf_map['PA'] = PA_Restaurent_MF
#     restaurent_mf_map['FL'] = FL_Restaurent_MF
#     restaurent_mf_map['TN'] = TN_Restaurent_MF
#     restaurent_mf_map['IN'] = IN_Restaurent_MF
#     restaurent_mf_map['MO'] = MO_Restaurent_MF
#     restaurent_mf_map['LA'] = LA_Restaurent_MF
#     restaurent_mf_map['AZ'] = AZ_Restaurent_MF
#     restaurent_mf_map['NJ'] = NJ_Restaurent_MF
#     restaurent_mf_map['NV'] = NV_Restaurent_MF
#     restaurent_mf_map['AB'] = AB_Restaurent_MF

#     nightlife_mf_map['PA'] = PA_Nightlife_MF
#     nightlife_mf_map['FL'] = FL_Nightlife_MF
#     nightlife_mf_map['TN'] = TN_Nightlife_MF
#     nightlife_mf_map['IN'] = IN_Nightlife_MF
#     nightlife_mf_map['MO'] = MO_Nightlife_MF
#     nightlife_mf_map['LA'] = LA_Nightlife_MF
#     nightlife_mf_map['AZ'] = AZ_Nightlife_MF
#     nightlife_mf_map['NJ'] = NJ_Nightlife_MF
#     nightlife_mf_map['NV'] = NV_Nightlife_MF
#     nightlife_mf_map['AB'] = AB_Nightlife_MF

#     hotel_aecf_map['PA'] = PA_Hotel_AECF
#     hotel_aecf_map['FL'] = FL_Hotel_AECF
#     hotel_aecf_map['TN'] = TN_Hotel_AECF
#     hotel_aecf_map['IN'] = IN_Hotel_AECF
#     hotel_aecf_map['MO'] = MO_Hotel_AECF
#     hotel_aecf_map['LA'] = LA_Hotel_AECF
#     hotel_aecf_map['AZ'] = AZ_Hotel_AECF
#     hotel_aecf_map['NJ'] = NJ_Hotel_AECF
#     hotel_aecf_map['NV'] = NV_Hotel_AECF
#     hotel_aecf_map['AB'] = AB_Hotel_AECF

#     restaurent_aecf_map['PA'] = PA_Restaurent_AECF
#     restaurent_aecf_map['FL'] = FL_Restaurent_AECF
#     restaurent_aecf_map['TN'] = TN_Restaurent_AECF
#     restaurent_aecf_map['IN'] = IN_Restaurent_AECF
#     restaurent_aecf_map['MO'] = MO_Restaurent_AECF
#     restaurent_aecf_map['LA'] = LA_Restaurent_AECF
#     restaurent_aecf_map['AZ'] = AZ_Restaurent_AECF
#     restaurent_aecf_map['NJ'] = NJ_Restaurent_AECF
#     restaurent_aecf_map['NV'] = NV_Restaurent_AECF
#     restaurent_aecf_map['AB'] = AB_Restaurent_AECF

#     nightlife_aecf_map['PA'] = PA_Nightlife_AECF
#     nightlife_aecf_map['FL'] = FL_Nightlife_AECF
#     nightlife_aecf_map['TN'] = TN_Nightlife_AECF
#     nightlife_aecf_map['IN'] = IN_Nightlife_AECF
#     nightlife_aecf_map['MO'] = MO_Nightlife_AECF
#     nightlife_aecf_map['LA'] = LA_Nightlife_AECF
#     nightlife_aecf_map['AZ'] = AZ_Nightlife_AECF
#     nightlife_aecf_map['NJ'] = NJ_Nightlife_AECF
#     nightlife_aecf_map['NV'] = NV_Nightlife_AECF
#     nightlife_aecf_map['AB'] = AB_Nightlife_AECF


@app.route('/<string:rec_type>/<string:state_name>/<int:user_id>/getNPR')
@cross_origin()
def getNPRRecommendation(rec_type, state_name, user_id):
    global hotel_state_rec_map
    global restaurent_state_rec_map
    global nightlife_state_rec_map
    print("HOTEL MAP SIZE:")
    print(len(hotel_state_rec_map))
    if (len(hotel_state_rec_map) == 0 or len(restaurent_state_rec_map) == 0 or
            len(nightlife_state_rec_map) == 0):
        helper_fun()

    if rec_type == "hotel":
        recommendations_class = hotel_state_rec_map[state_name]
    elif rec_type == "restaurent":
        recommendations_class = restaurent_state_rec_map[state_name]
    elif rec_type == "nightlife":
        recommendations_class = nightlife_state_rec_map[state_name]

    business_list = recommendations_class.getNPRForuUser(user_id)
    return json.dumps(
        [{'name': business.name, 'address': business.address, 'city': business.city, 'state': business.state, 'postal_code': business.postal_code, 'stars': business.stars} for business in business_list])


@app.route('/<int:user_id>/getNPR2')
@cross_origin()
def getNPRR2ecommendation(user_id):
    global hotel_state_df_map
    global reviews_df
    recommendation_class = LA_Hotel_Recommendation
    business_list = recommendation_class.getNPRForuUser(user_id)
    return json.dumps(
        [{'name': business.name, 'address': business.address, 'city': business.city, 'state': business.state, 'postal_code': business.postal_code, 'stars': business.stars} for business in business_list])


@app.route('/<string:rec_type>/<string:state_name>/<int:user_id>/getMF')
@cross_origin()
def getMFRecommendation(rec_type, state_name, user_id):
    global hotel_mf_map
    global restaurent_mf_map
    global nightlife_mf_map
    global hotel_state_rec_map
    global restaurent_state_rec_map
    global nightlife_state_rec_map
    if (len(hotel_mf_map) or len(restaurent_mf_map) or
        len(nightlife_mf_map) or len(hotel_state_rec_map) == 0 or
        len(restaurent_state_rec_map) == 0 or
            len(nightlife_state_rec_map) == 0):
        helper_fun()

    if rec_type == "hotel":
        mf_recommendations = hotel_mf_map[state_name]
        recommendations_class = hotel_state_rec_map[state_name]
    elif rec_type == "restaurent":
        mf_recommendations = restaurent_mf_map[state_name]
        recommendations_class = restaurent_state_rec_map[state_name]
    elif rec_type == "nightlife":
        mf_recommendations = nightlife_mf_map[state_name]
        recommendations_class = nightlife_state_rec_map[state_name]

    business_ids = mf_recommendations[user_id][:12]

    business_list = []
    for i in range(12):
        business_hash = recommendations_class.getBusinessHashFromBusinessNum(
            business_ids[i])
        business = recommendations_class.getBusinessInfo(business_hash)
        business_list.append(business)

    return json.dumps(
        [{'name': business.name, 'address': business.address, 'city': business.city, 'state': business.state, 'postal_code': business.postal_code, 'stars': business.stars} for business in business_list])


@app.route('/<string:rec_type>/<string:state_name>/<int:user_id>/getAECF')
@cross_origin()
def getAECFRecommendation(rec_type, state_name, user_id):
    global hotel_aecf_map
    global restaurent_aecf_map
    global nightlife_aecf_map
    global hotel_state_rec_map
    global restaurent_state_rec_map
    global nightlife_state_rec_map

    if (len(hotel_aecf_map) or len(restaurent_aecf_map) or
        len(nightlife_aecf_map) or len(hotel_state_rec_map) == 0 or
        len(restaurent_state_rec_map) == 0 or
            len(nightlife_state_rec_map) == 0):
        helper_fun()

    if rec_type == "hotel":
        aecf_recommendations = hotel_aecf_map[state_name]
        recommendations_class = hotel_state_rec_map[state_name]
    elif rec_type == "restaurent":
        aecf_recommendations = restaurent_aecf_map[state_name]
        recommendations_class = restaurent_state_rec_map[state_name]
    elif rec_type == "nightlife":
        aecf_recommendations = nightlife_aecf_map[state_name]
        recommendations_class = nightlife_state_rec_map[state_name]

    business_ids = aecf_recommendations.get_user_recommendation(user_id)
    # print(business_ids)

    business_list = []
    for i in range(12):
        business_hash = recommendations_class.getBusinessHashFromBusinessNum(
            business_ids[i])
        business = recommendations_class.getBusinessInfo(business_hash)
        business_list.append(business)

    return json.dumps(
        [{'name': business.name, 'address': business.address, 'city': business.city, 'state': business.state, 'postal_code': business.postal_code, 'stars': business.stars} for business in business_list])


if __name__ == '__main__':
    class Recommendations:
        def __init__(self, business_df, reviews_df, state_name, shorten=False):
            print(f"========Calculating For {state_name} State========")
            self.business_df = business_df
            self.reviews_df = reviews_df
            self.ratings_mat = []
            self.shorten = shorten if isinstance(shorten, bool) else False
            self.user_num_to_user_hash_dict = dict()
            self.user_hash_to_user_num_dict = dict()
            self.business_num_to_business_hash_dict = dict()
            self.business_hash_to_business_num_dict = dict()
            self.business_recommendations = []
            self.business_popularity = []
            self.calculateRatingMatrix()
            self.nonPersonalizedRecommendations()

        def calculateRatingMatrix(self):
            print("Calculating rating matrix...")
            business_list = list(self.business_df['business_id'])
            reviews_df_updated = self.reviews_df[self.reviews_df['business_id'].isin(
                business_list)]

            if (self.shorten):
                print(
                    f"Size Before Cutting Down: {reviews_df_updated.shape[0]}")
                user_counts = reviews_df_updated.groupby(
                    'user_id').size().reset_index(name='count')

                # Sort the user_counts dataframe in descending order by count and select the top 100 user_ids
                top_users = user_counts.sort_values(by='count', ascending=False).head(100)[
                    'user_id'].tolist()

                # Filter the original dataframe to keep only the records that belong to the top 100 user_ids
                reviews_df_updated = reviews_df_updated[reviews_df_updated['user_id'].isin(
                    top_users)]
                print(
                    f"Size After Cutting Down: {reviews_df_updated.shape[0]}")

            unique_business_id = reviews_df_updated['business_id'].unique()
            unique_user_id = reviews_df_updated['user_id'].unique()

            j = 0
            for u in unique_user_id:
                self.user_hash_to_user_num_dict[u] = j
                self.user_num_to_user_hash_dict[j] = u
                j += 1

            j = 0
            for i in unique_business_id:
                self.business_hash_to_business_num_dict[i] = j
                self.business_num_to_business_hash_dict[j] = i
                j += 1

            # Then, use the generated dictionaries to reindex UserID and MovieID in the data_df
            user_list = reviews_df_updated['user_id'].values
            movie_list = reviews_df_updated['business_id'].values
            for j in range(len(reviews_df_updated)):
                user_list[j] = self.user_hash_to_user_num_dict[user_list[j]]
                movie_list[j] = self.business_hash_to_business_num_dict[movie_list[j]]
            reviews_df_updated['user_id'] = user_list
            reviews_df_updated['business_id'] = movie_list

            num_user = len(reviews_df_updated['user_id'].unique())
            num_movie = len(reviews_df_updated['business_id'].unique())

            self.ratings_mat = coo_matrix((reviews_df_updated['stars'].values, (reviews_df_updated['user_id'].values,
                                                                                reviews_df_updated['business_id'].values)), shape=(num_user, num_movie)).astype(float).toarray()
            print(
                f"Size of Ratings Matrix: {self.ratings_mat.shape[0]}, {self.ratings_mat.shape[1]}")

        def nonPersonalizedRecommendations(self):
            print("Calculating NPR...")
            n = len(self.ratings_mat)  # number of users
            m = len(self.ratings_mat[0])  # number of movies

            # Creating popularity array - size number of movies
            self.business_popularity = np.zeros((m,))
            # claculating the popularity of each movie by summing the values in each column
            self.business_popularity = self.ratings_mat.sum(axis=0)

            self.business_recommendations = np.zeros((n, 50), dtype=np.int32)

            for u in range(self.ratings_mat.shape[0]):
                business_unvisited = np.where(self.ratings_mat[u] == 0)[0]
                unwatched_popularity = self.business_popularity[business_unvisited]
                # Sort the unwatched movies according to popularity and fetch top 50 to recommend
                self.business_recommendations[u] = business_unvisited[np.argsort(
                    unwatched_popularity)[::-1]][:50]

        def getNPRForuUser(self, user_num):
            print(f"Non personalized recommendations for User {user_num}:")
            business_list = []
            for i in range(12):
                business_hash = self.getBusinessHashFromBusinessNum(
                    self.business_recommendations[0, i])
                business = self.getBusinessInfo(business_hash)
                business_list.append(business)
            return business_list

        def getUserHashFromUserNum(self, user_num):
            return self.user_num_to_user_hash_dict[user_num]

        def getUserNumFromUserHash(self, user_hash):
            return self.user_hash_to_user_num_dict[user_hash]

        def getBusinessHashFromBusinessNum(self, business_num):
            return self.business_num_to_business_hash_dict[business_num]

        def getBusinessNumFromBusinessHash(self, business_hash):
            return self.business_hash_to_business_num_dict[business_hash]

        def getBusinessInfo(self, business_hash):
            bus_df = self.business_df[self.business_df['business_id']
                                      == business_hash].iloc[0]
            return Business(bus_df['name'], bus_df['address'], bus_df['city'], bus_df['state'], bus_df['postal_code'], bus_df['stars'])

    # hotel_state_rec_map
    #
    # restaurent_state_rec_map
    #
    # nightlife_state_rec_map
    #
    # global hotel_mf_map
    #
    # global restaurent_mf_map
    #
    # global nightlife_mf_map
    #
    # global hotel_aecf_map
    #
    # global restaurent_aecf_map
    #
    # global nightlife_aecf_map
    # print("Loading Hotel Data Files...")
    # print(datetime.datetime.now())
    # PA_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/PA_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['PA'] = PA_Hotel_Recommendation
    # FL_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/FL_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['FL'] = FL_Hotel_Recommendation
    # TN_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/TN_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['TN'] = TN_Hotel_Recommendation
    # IN_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/IN_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['IN'] = IN_Hotel_Recommendation
    # MO_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/MO_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['MO'] = MO_Hotel_Recommendation
    # LA_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/LA_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['LA'] = LA_Hotel_Recommendation
    # AZ_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/AZ_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['AZ'] = AZ_Hotel_Recommendation
    # NJ_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/NJ_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['NJ'] = NJ_Hotel_Recommendation
    # NV_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/NV_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['NV'] = NV_Hotel_Recommendation
    # AB_Hotel_Recommendation = decompress_pickle(
    #     "data/hotel/AB_Hotel_Recommendation.pbz2")
    # # hotel_state_rec_map['AB'] = AB_Hotel_Recommendation
    # print("Loading Hotel Data Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Restaurent Data Files...")
    # print(datetime.datetime.now())
    # PA_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/PA_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['PA'] = PA_Restaurent_Recommendation
    # FL_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/FL_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['FL'] = FL_Restaurent_Recommendation
    # TN_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/TN_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['TN'] = TN_Restaurent_Recommendation
    # IN_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/IN_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['IN'] = IN_Restaurent_Recommendation
    # MO_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/MO_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['MO'] = MO_Restaurent_Recommendation
    # LA_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/LA_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['LA'] = LA_Restaurent_Recommendation
    # AZ_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/AZ_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['AZ'] = AZ_Restaurent_Recommendation
    # NJ_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/NJ_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['NJ'] = NJ_Restaurent_Recommendation
    # NV_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/NV_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['NV'] = NV_Restaurent_Recommendation
    # AB_Restaurent_Recommendation = decompress_pickle(
    #     "data/restaurent/AB_Restaurent_Recommendation.pbz2")
    # # restaurent_state_rec_map['AB'] = AB_Restaurent_Recommendation
    # print("Loading Restaurent Data Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Nightlife Data Files...")
    # print(datetime.datetime.now())
    # PA_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/PA_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['PA'] = PA_Nightlife_Recommendation
    # FL_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/FL_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['FL'] = FL_Nightlife_Recommendation
    # TN_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/TN_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['TN'] = TN_Nightlife_Recommendation
    # IN_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/IN_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['IN'] = IN_Nightlife_Recommendation
    # MO_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/MO_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['MO'] = MO_Nightlife_Recommendation
    # LA_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/LA_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['LA'] = LA_Nightlife_Recommendation
    # AZ_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/AZ_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['AZ'] = AZ_Nightlife_Recommendation
    # NJ_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/NJ_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['NJ'] = NJ_Nightlife_Recommendation
    # NV_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/NV_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['NV'] = NV_Nightlife_Recommendation
    # AB_Nightlife_Recommendation = decompress_pickle(
    #     "data/nightlife/AB_Nightlife_Recommendation.pbz2")
    # # nightlife_state_rec_map['AB'] = AB_Nightlife_Recommendation
    # print("Loading Nightlife Data Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Hotel MF Files...")
    # print(datetime.datetime.now())
    # PA_Hotel_MF = decompress_pickle("data/hotel/PA_Hotel_MF.pbz2")
    # # hotel_mf_map['PA'] = PA_Hotel_MF
    # FL_Hotel_MF = decompress_pickle("data/hotel/FL_Hotel_MF.pbz2")
    # # hotel_mf_map['FL'] = FL_Hotel_MF
    # TN_Hotel_MF = decompress_pickle("data/hotel/TN_Hotel_MF.pbz2")
    # # hotel_mf_map['TN'] = TN_Hotel_MF
    # IN_Hotel_MF = decompress_pickle("data/hotel/IN_Hotel_MF.pbz2")
    # # hotel_mf_map['IN'] = IN_Hotel_MF
    # MO_Hotel_MF = decompress_pickle("data/hotel/MO_Hotel_MF.pbz2")
    # # hotel_mf_map['MO'] = MO_Hotel_MF
    # LA_Hotel_MF = decompress_pickle("data/hotel/LA_Hotel_MF.pbz2")
    # # hotel_mf_map['LA'] = LA_Hotel_MF
    # AZ_Hotel_MF = decompress_pickle("data/hotel/AZ_Hotel_MF.pbz2")
    # # hotel_mf_map['AZ'] = AZ_Hotel_MF
    # NJ_Hotel_MF = decompress_pickle("data/hotel/NJ_Hotel_MF.pbz2")
    # # hotel_mf_map['NJ'] = NJ_Hotel_MF
    # NV_Hotel_MF = decompress_pickle("data/hotel/NV_Hotel_MF.pbz2")
    # # hotel_mf_map['NV'] = NV_Hotel_MF
    # AB_Hotel_MF = decompress_pickle("data/hotel/AB_Hotel_MF.pbz2")
    # # hotel_mf_map['AB'] = AB_Hotel_MF
    # print("Loading Hotel MF Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Restaurent MF Files...")
    # print(datetime.datetime.now())
    # PA_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/PA_Restaurent_MF.pbz2")
    # # restaurent_mf_map['PA'] = PA_Restaurent_MF
    # FL_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/FL_Restaurent_MF.pbz2")
    # # restaurent_mf_map['FL'] = FL_Restaurent_MF
    # TN_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/TN_Restaurent_MF.pbz2")
    # # restaurent_mf_map['TN'] = TN_Restaurent_MF
    # IN_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/IN_Restaurent_MF.pbz2")
    # # restaurent_mf_map['IN'] = IN_Restaurent_MF
    # MO_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/MO_Restaurent_MF.pbz2")
    # # restaurent_mf_map['MO'] = MO_Restaurent_MF
    # LA_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/LA_Restaurent_MF.pbz2")
    # # restaurent_mf_map['LA'] = LA_Restaurent_MF
    # AZ_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/AZ_Restaurent_MF.pbz2")
    # # restaurent_mf_map['AZ'] = AZ_Restaurent_MF
    # NJ_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/NJ_Restaurent_MF.pbz2")
    # # restaurent_mf_map['NJ'] = NJ_Restaurent_MF
    # NV_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/NV_Restaurent_MF.pbz2")
    # # restaurent_mf_map['NV'] = NV_Restaurent_MF
    # AB_Restaurent_MF = decompress_pickle(
    #     "data/restaurent/AB_Restaurent_MF.pbz2")
    # # restaurent_mf_map['AB'] = AB_Restaurent_MF
    # print("Loading Restaurent MF Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Nightlife MF Files...")
    # print(datetime.datetime.now())
    # PA_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/PA_Nightlife_MF.pbz2")
    # # nightlife_mf_map['PA'] = PA_Nightlife_MF
    # FL_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/FL_Nightlife_MF.pbz2")
    # # nightlife_mf_map['FL'] = FL_Nightlife_MF
    # TN_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/TN_Nightlife_MF.pbz2")
    # # nightlife_mf_map['TN'] = TN_Nightlife_MF
    # IN_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/IN_Nightlife_MF.pbz2")
    # # nightlife_mf_map['IN'] = IN_Nightlife_MF
    # MO_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/MO_Nightlife_MF.pbz2")
    # # nightlife_mf_map['MO'] = MO_Nightlife_MF
    # LA_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/LA_Nightlife_MF.pbz2")
    # # nightlife_mf_map['LA'] = LA_Nightlife_MF
    # AZ_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/AZ_Nightlife_MF.pbz2")
    # # nightlife_mf_map['AZ'] = AZ_Nightlife_MF
    # NJ_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/NJ_Nightlife_MF.pbz2")
    # # nightlife_mf_map['NJ'] = NJ_Nightlife_MF
    # NV_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/NV_Nightlife_MF.pbz2")
    # # nightlife_mf_map['NV'] = NV_Nightlife_MF
    # AB_Nightlife_MF = decompress_pickle(
    #     "data/nightlife/AB_Nightlife_MF.pbz2")
    # # nightlife_mf_map['AB'] = AB_Nightlife_MF
    # print("Loading Nightlife MF Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Hotel AECF Files...")
    # print(datetime.datetime.now())
    # PA_Hotel_AECF = decompress_pickle(
    #     "data/hotel/PA_Hotel_AECF.pbz2")
    # # hotel_aecf_map['PA'] = PA_Hotel_AECF
    # FL_Hotel_AECF = decompress_pickle(
    #     "data/hotel/FL_Hotel_AECF.pbz2")
    # # hotel_aecf_map['FL'] = FL_Hotel_AECF
    # TN_Hotel_AECF = decompress_pickle(
    #     "data/hotel/TN_Hotel_AECF.pbz2")
    # # hotel_aecf_map['TN'] = TN_Hotel_AECF
    # IN_Hotel_AECF = decompress_pickle(
    #     "data/hotel/IN_Hotel_AECF.pbz2")
    # # hotel_aecf_map['IN'] = IN_Hotel_AECF
    # MO_Hotel_AECF = decompress_pickle(
    #     "data/hotel/MO_Hotel_AECF.pbz2")
    # # hotel_aecf_map['MO'] = MO_Hotel_AECF
    # LA_Hotel_AECF = decompress_pickle(
    #     "data/hotel/LA_Hotel_AECF.pbz2")
    # # hotel_aecf_map['LA'] = LA_Hotel_AECF
    # AZ_Hotel_AECF = decompress_pickle(
    #     "data/hotel/AZ_Hotel_AECF.pbz2")
    # # hotel_aecf_map['AZ'] = AZ_Hotel_AECF
    # NJ_Hotel_AECF = decompress_pickle(
    #     "data/hotel/NJ_Hotel_AECF.pbz2")
    # # hotel_aecf_map['NJ'] = NJ_Hotel_AECF
    # NV_Hotel_AECF = decompress_pickle(
    #     "data/hotel/NV_Hotel_AECF.pbz2")
    # # hotel_aecf_map['NV'] = NV_Hotel_AECF
    # AB_Hotel_AECF = decompress_pickle(
    #     "data/hotel/AB_Hotel_AECF.pbz2")
    # # hotel_aecf_map['AB'] = AB_Hotel_AECF
    # print("Loading Hotel AECF Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Restaurent AECF Files...")
    # print(datetime.datetime.now())
    # PA_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/PA_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['PA'] = PA_Restaurent_AECF
    # FL_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/FL_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['FL'] = FL_Restaurent_AECF
    # TN_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/TN_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['TN'] = TN_Restaurent_AECF
    # IN_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/IN_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['IN'] = IN_Restaurent_AECF
    # MO_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/MO_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['MO'] = MO_Restaurent_AECF
    # LA_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/LA_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['LA'] = LA_Restaurent_AECF
    # AZ_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/AZ_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['AZ'] = AZ_Restaurent_AECF
    # NJ_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/NJ_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['NJ'] = NJ_Restaurent_AECF
    # NV_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/NV_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['NV'] = NV_Restaurent_AECF
    # AB_Restaurent_AECF = decompress_pickle(
    #     "data/restaurent/AB_Restaurent_AECF.pbz2")
    # # restaurent_aecf_map['AB'] = AB_Restaurent_AECF
    # print("Loading Restaurent AECF Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")

    # print("Loading Nightlife AECF Files...")
    # print(datetime.datetime.now())
    # PA_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/PA_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['PA'] = PA_Nightlife_AECF
    # FL_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/FL_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['FL'] = FL_Nightlife_AECF
    # TN_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/TN_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['TN'] = TN_Nightlife_AECF
    # IN_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/IN_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['IN'] = IN_Nightlife_AECF
    # MO_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/MO_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['MO'] = MO_Nightlife_AECF
    # LA_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/LA_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['LA'] = LA_Nightlife_AECF
    # AZ_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/AZ_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['AZ'] = AZ_Nightlife_AECF
    # NJ_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/NJ_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['NJ'] = NJ_Nightlife_AECF
    # NV_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/NV_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['NV'] = NV_Nightlife_AECF
    # AB_Nightlife_AECF = decompress_pickle(
    #     "data/nightlife/AB_Nightlife_AECF.pbz2")
    # # nightlife_aecf_map['AB'] = AB_Nightlife_AECF
    # print("Loading Nightlife AECF Files Completed...")
    # print(datetime.datetime.now())
    # print("\n")
    # helper_fun()
    app.run()
