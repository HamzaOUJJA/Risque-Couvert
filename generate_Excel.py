import pandas as pd
from colorama import Fore, Style, init
from Other.Colorate import Colorate

init(autoreset=True)
color_etape = Fore.CYAN + Style.BRIGHT
color_desc = Fore.YELLOW

def generate_Excel(
    df_All_MKD_Spreads,
    df_DETAIL_POUR_COMPTA,
    df_Perimetre_and_Whopper,
    df_Perimetre_and_Whopper_gby,
    df_Whopper_explain,
    df_Whopper_explain_gby,
    df_Comparaison_Explain,
    tcd_m1_fmt,
    tcd_m2_fmt,
    tcd_explain_fmt
):
    dfs_and_sheets = [
        (df_All_MKD_Spreads, 'All_MKD_Spreads'),
        (df_DETAIL_POUR_COMPTA, 'DETAIL_POUR_COMPTA'),
        (df_Perimetre_and_Whopper, 'Perimetre_and_Whopper'),
        (df_Perimetre_and_Whopper_gby, 'Perimetre_and_Whopper_gby'),
        (df_Whopper_explain, 'Whopper_explain'),
        (df_Whopper_explain_gby, 'Whopper_explain_gby'),
        (df_Comparaison_Explain, 'Comparaison_Explain'),
    ]

    total = len(dfs_and_sheets)

    with pd.ExcelWriter('Risque Couvert.xlsx', engine='openpyxl') as writer:
        for i, (df, sheet) in enumerate(dfs_and_sheets, start=1):
            df.to_excel(writer, sheet_name=sheet, index=False)
            percent = int(i / total * 100)
            print(f"\r{color_etape}Etape 11 :  {color_desc}Écriture des DataFrames dans Risque Couvert.xlsx ... {percent}%", end='', flush=True)

        current_row = 1

        # Titre et tcd_m1_fmt
        pd.DataFrame([["Comparaison M1"]]).to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row, index=False, header=False)
        current_row += 1
        tcd_m1_fmt.to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row)
        current_row += len(tcd_m1_fmt) + 2

        # Titre et tcd_m2_fmt
        pd.DataFrame([["Comparaison M2"]]).to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row, index=False, header=False)
        current_row += 1
        tcd_m2_fmt.to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row)
        current_row += len(tcd_m2_fmt) + 2

        # Titre et tcd_explain_fmt
        pd.DataFrame([["M2 - M1"]]).to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row, index=False, header=False)
        current_row += 1
        pd.DataFrame([["Explain M2 - M1"]]).to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row, index=False, header=False)
        current_row += 1
        tcd_explain_fmt.to_excel(writer, sheet_name="TCD - comparaison & explain", startrow=current_row)
        
    print()

    print(f"{color_etape}Etape 12 :  {color_desc}Ajuster et Colorer les Colonnes...")
    Colorate()

    print(Fore.GREEN + Style.BRIGHT + "Traitement terminé avec succès !")