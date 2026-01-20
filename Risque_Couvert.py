import pandas as pd


def Risque_Couvert(date_1, date_2):

    df_All_MKD_Spreads = pd.read_csv('file.txt', sep='\t', decimal=',')
    tcd_m1_fmt = pd.read_csv('tcd_m1_fmt.txt', sep='\t', decimal=',')
    tcd_m2_fmt = pd.read_csv('tcd_m2_fmt.txt', sep='\t', decimal=',')
    tcd_explain_fmt = pd.read_csv('tcd_explain_fmt.txt', sep='\t', decimal=',')

    

    return (
        df_All_MKD_Spreads,
        tcd_m1_fmt,
        tcd_m2_fmt,
        tcd_explain_fmt
    )

