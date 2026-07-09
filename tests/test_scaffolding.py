import os
import pandas as pd

def test_files_exist():
    assert os.path.exists("data/custos_financeiros.csv")
    assert os.path.exists("data/logs_operacionais.csv")

def test_load_csv_files():
    cf_df = pd.read_csv("data/custos_financeiros.csv")
    lo_df = pd.read_csv("data/logs_operacionais.csv")
    
    assert "produto_id" in cf_df.columns
    assert "produto_id" in lo_df.columns
    assert len(cf_df) == 3
    assert len(lo_df) == 3
