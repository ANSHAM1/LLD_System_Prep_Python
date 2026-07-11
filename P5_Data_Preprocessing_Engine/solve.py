from P4_Data_Cleaning_Engine.solve import Database, DataCleaner

from datasets import load_dataset # type: ignore
# from typing import cast
import pandas as pd

class DataPreProcessor:
    TrainTok       : list[tuple[list[str], int]]
    TestTok        : list[tuple[list[str], int]]
    ValidateTok    : list[tuple[list[str], int]]

    Vocab          : dict[str, int]
    Vocab_IDs      : dict[str, int]

    TrainTokIDs    : list[tuple[list[int], int]]
    TestTokIDs     : list[tuple[list[int], int]]
    ValidateTokIDs : list[tuple[list[int], int]]

    def __init__(self) -> None:
        self.TrainTok    = []
        self.TestTok     = []
        self.ValidateTok = []

        self.Vocab       = {}
        self.Vocab_IDs   = {"<PAD>": 0, "<UNK>": 1}

    def __process_dataset(self, df : pd.DataFrame) -> list[tuple[list[str], int]]:
        result : list[tuple[list[str], int]] = []

        for row in df.itertuples(index=False):
            tokens = row.text.split()                               # type: ignore
            for token in tokens:                                    # type: ignore
                self.Vocab[token] = self.Vocab.get(token, 0) + 1    # type: ignore
            result.append((tokens, row.label))                      # type: ignore

        return result

    def tokenize(self, DC: DataCleaner) -> None:
        self.TrainTok    = self.__process_dataset(DC.Train)
        self.TestTok     = self.__process_dataset(DC.Test)
        self.ValidateTok = self.__process_dataset(DC.Validate)

        self.Vocab = dict(sorted(self.Vocab.items(), key=lambda x: (-x[1], x[0]))) 
        for idx, (word, _) in enumerate(sorted(self.Vocab.items(), key=lambda x: (-x[1], x[0])), start=2):
            self.Vocab_IDs[word] = idx

        print("Data Tokenization and Vocabulary Building Completed Successfully")

    def generateStatistics(self) -> None:
        TTokenCount = sum(self.Vocab.values())
        UTokenCount = len(self.Vocab)

        NoSentences = len(self.TrainTok) + len(self.TestTok) + len(self.ValidateTok)
        AvgTokenSen = TTokenCount / NoSentences if NoSentences else 0

        MxSenLength = 0
        MnSenLength = float('inf')

        for dataset in (self.TrainTok, self.TestTok, self.ValidateTok):
            for tokens, _ in dataset:
                length = len(tokens)
                MxSenLength = max(MxSenLength, length)
                MnSenLength = min(MnSenLength, length)

        if MnSenLength == float('inf'):
            MnSenLength = 0

        print("=" * 60)
        print("               DATASET STATISTICS")
        print("=" * 60)
        print(f"{'Total Sentences':<30}: {NoSentences}")
        print(f"{'Total Tokens':<30}: {TTokenCount}")
        print(f"{'Unique Tokens':<30}: {UTokenCount}")
        print(f"{'Average Tokens/Sentence':<30}: {AvgTokenSen:.2f}")
        print(f"{'Maximum Sentence Length':<30}: {MxSenLength}")
        print(f"{'Minimum Sentence Length':<30}: {MnSenLength}")
        print("=" * 60)

        print("\nTop 50 Vocabulary Words By Frequency")
        print("-" * 60)
        for i, (word, freq) in enumerate(self.Vocab.items(), start=1):
            if i > 50:
                break
            print(f"{i:2}. {word:<20} : {freq}")

        print("\nBottom 50 Vocabulary Words By Frequency")
        print("-" * 60)
        for i, (word, freq) in enumerate(sorted(self.Vocab.items(), key=lambda x: (x[1], x[0])), start=1):
            if i > 50:
                break
            print(f"{i:2}. {word:<20} : {freq}")

    def __token_to_ids_list(self, Tlist : list[tuple[list[str], int]]) -> list[tuple[list[int], int]]:
        return [([self.Vocab_IDs.get(token, 1) for token in tokens], label) for tokens, label in Tlist]

    def token_to_ids(self) -> None:
        self.TrainTokIDs    = self.__token_to_ids_list(self.TrainTok) 
        self.TestTokIDs     = self.__token_to_ids_list(self.TestTok) 
        self.ValidateTokIDs = self.__token_to_ids_list(self.ValidateTok)

        print("Token IDs generated successfully")

    def __pad_and_tranc_list(self, Tlist : list[tuple[list[int], int]], size : int) -> list[tuple[list[int], int]]:
        updatedIDs : list[tuple[list[int], int]] = []
        for (ids, label) in Tlist:
            _ids = ids.copy()

            if len(ids) > size:
                _ids = _ids[: size]
            else:
                _ids.extend([0] * (size - len(_ids)))
            
            updatedIDs.append((_ids, label))
        
        return updatedIDs

    def pad_and_tranc(self, size : int) -> None:
        self.TrainTokIDs    = self.__pad_and_tranc_list(self.TrainTokIDs, size)
        self.TestTokIDs     = self.__pad_and_tranc_list(self.TestTokIDs, size)
        self.ValidateTokIDs = self.__pad_and_tranc_list(self.ValidateTokIDs, size)

        print("Padding and Truncation Done Successfully")


Dataset = load_dataset("dair-ai/emotion")

def main(DB : Database) -> None:
    DC : DataCleaner = DataCleaner()
    DC.split_store(Dataset)
    DC.clean_data(0.05)

    DP : DataPreProcessor = DataPreProcessor()
    DP.tokenize(DC)
    DP.generateStatistics()
    DP.token_to_ids()
    DP.pad_and_tranc(32)


if __name__ == "__main__":
    DB : Database = Database()
    if DB.connect():
        print("Database Connected successfully!")
        main(DB) 
    else:
        print("Connection Error")