from datasets import  DatasetDict, load_dataset # type: ignore
from typing import cast
import pandas as pd
import pyodbc

class DataLib:
    @staticmethod
    def clean(df : pd.DataFrame, limit : float = 0) -> pd.DataFrame:
        if limit < 0 or limit > 1:
            raise ValueError("limit value should be between 0 and 1")
        
        df.dropna(subset=["text"], inplace=True)
        if df['label'].isna().sum()/len(df) <= limit:
            df.dropna(inplace=True)
        else:
            df.fillna(df.mode(), inplace=True)

        df.drop_duplicates(inplace=True)
        df = df[df["label"].between(0, 5)]

        df["label"] = df["label"].astype(int)
        df["text"] = df["text"].str.strip()
        df["text"] = df["text"].str.lower()

        df["text"] = df["text"].str.replace(r"[^a-zA-Z0-9\s]","",regex=True)

        return df
    
    @staticmethod
    def preprocess(df : pd.DataFrame) -> pd.DataFrame:
        return df
        

class DataPreprocess:
    Train    : pd.DataFrame
    Test     : pd.DataFrame
    Validate : pd.DataFrame

    def __init__(self) -> None:
        pass

    def split_store(self, dataset : DatasetDict) -> None:
        self.Train    =  cast(pd.DataFrame, dataset["train"].to_pandas())
        self.Test     =  cast(pd.DataFrame, dataset["test"].to_pandas())
        self.Validate =  cast(pd.DataFrame, dataset["validation"].to_pandas())

        print("data loaded successfully in memeory")
        print()

    def clean_data(self, limit : float):
        if limit < 0 or limit > 1:
            raise ValueError("limit value should be between 0 and 1")
        
        self.Train    = DataLib.clean(self.Train, limit)
        print("Training Data Cleaned Successfully")
        self.Test     = DataLib.clean(self.Test, limit)
        print("Testing Data Cleaned Successfully")
        self.Validate = DataLib.clean(self.Validate, limit)
        print("validation Data Cleaned Successfully")

    def label_statistics(self) -> None:
        print("sample statistics per label")
        most_common : int = 0
        check : int = 0
        for i in range(0, 6):
            print("label : ", i)
            samples : int = len(self.Train[self.Train["label"] == i]) + len(self.Test[self.Test["label"] == i]) + len(self.Validate[self.Validate["label"] == i])
            totals : int = len(self.Train) + len(self.Test) + len(self.Validate)
            print("   no of samples : ", samples)
            print("   percentage per label : ", samples/totals * 100)

            if check < samples:
                check = samples
                most_common = i

        print("most common type label is : ", most_common)
    

    def dataset_info(self) -> None:
        print("==================Dataset Info==================")
        print("Training Dataset :")
        print("    Columns      : ", self.Train.columns)
        print("    Dimension    : ", len(self.Train) , "x" , 2)
        print("    Memory Usage : ", self.Train.memory_usage())
        print("    Description  : ", self.Train.describe())
        print()
        print("Testing Dataset :")
        print("    Columns      : ", self.Test.columns)
        print("    Dimension    : ", len(self.Test) , "x" , 2)
        print("    Memory Usage : ", self.Test.memory_usage())
        print("    Description  : ", self.Test.describe())
        print()
        print("Validation Dataset :")
        print("    Columns      : ", self.Validate.columns)
        print("    Dimension    : ", len(self.Validate) , "x" , 2)
        print("    Memory Usage : ", self.Validate.memory_usage())
        print("    Description  : ", self.Validate.describe())
        print("================================================")

class Database:
    __conn : pyodbc.Connection
    __cursor : pyodbc.Cursor

    def __init__(self) -> None:
        pass

    def connect(self) -> bool:
        self.__conn = pyodbc.connect(
                "DRIVER={ODBC Driver 18 for SQL Server};"
                "SERVER=.;"
                "DATABASE=PythonDB;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
                )
        
        if self.__conn:
            self.__cursor = self.__conn.cursor()
            return True
        return False
    
    def createTable(self, tname : str) -> None:
        if self.table_exists(tname):
            return
        
        self.__cursor.execute(f"""
            CREATE TABLE {tname} (
                text NVARCHAR(MAX),
                label INT
            )
        """)

        self.__conn.commit()
        print("Table created successfully!")

    def table_exists(self, table_name: str) -> bool:
        self.__cursor.execute("""
            SELECT 1
            WHERE OBJECT_ID(?, 'U') IS NOT NULL
        """, table_name)

        return self.__cursor.fetchone() is not None
    
    def insertInto(self, tname: str, df: pd.DataFrame) -> None:
        rows = list(df[["text", "label"]].itertuples(index=False, name=None))

        query = f"""
            INSERT INTO [{tname}] ([text], [label])
            VALUES (?, ?)
        """

        self.__cursor.executemany(query, rows) # type: ignore
        self.__conn.commit()

    def selectQuery(self, query : str) -> pd.DataFrame:
        query = query.lstrip()
        if not query.lower().startswith("select"):
            raise SyntaxError("Only SELECT queries are allowed")
        
        return pd.read_sql(query, self.__conn) # type: ignore
    
    def disconnect(self) -> None:
        self.__conn.close()
        print("Database Disconnected successfully!")

Dataset = load_dataset("dair-ai/emotion")

def main(DB : Database):
    DPp : DataPreprocess = DataPreprocess()
    DPp.split_store(Dataset)
    DPp.dataset_info()

    print()

    DPp.clean_data(0.05)
    print()
    DPp.label_statistics()

    DB.createTable("Training")
    # DB.insertInto("Training", DPp.Train)

    DB.createTable("Testing")
    # DB.insertInto("Training", DPp.Test)

    DB.createTable("Validation")
    # DB.insertInto("Training", DPp.Validate)

    query : str = """
        SELECT 
            TEXT
        FROM TRAINING
        WHERE LABEL = 1
    """
    print(DB.selectQuery(query))


if __name__ == "__main__":
    DB : Database = Database()
    if DB.connect():
        print("Database Connected successfully!")
        main(DB) 
    else:
        print("Connection Error")