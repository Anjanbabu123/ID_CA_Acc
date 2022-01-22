from pathlib import Path
import warnings

import pandas as pd


warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def load_data(path: Path) -> dict[str, pd.DataFrame]:
    FILE_NAME = "P&L 20-21-22.xlsx"

    data_path = path / FILE_NAME

    return pd.read_excel(data_path, sheet_name=None, header=None)


def truncate_df(df: pd.DataFrame) -> pd.DataFrame:
    threshold = df.shape[1] // 2
    return df.dropna(axis=0, how="any", thresh=threshold).reset_index(drop=True)


def process_data(sheet_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    terminal_index = None
    for idx, header in enumerate(df.iloc[1].values[1:]):
        if terminal_index is None and pd.isnull(header):
            terminal_index = idx
            continue

    project_df = df.iloc[2:3, 1:terminal_index].reset_index(drop=True)
    project_df.columns = df.iloc[1, 1:terminal_index]
    project_df["Sheet Name"] = sheet_name

    separation_index = None
    terminal_index = None
    for idx, header in enumerate(df.iloc[4].values):
        if separation_index is None and pd.isnull(header):
            separation_index = idx
            continue

        if terminal_index is None and pd.isnull(header):
            terminal_index = idx
            break

    receipt_df = truncate_df(df.iloc[5:, :separation_index].reset_index(drop=True))
    receipt_df.columns = df.iloc[4, :separation_index]
    receipt_df["Sheet Name"] = sheet_name
    receipt_df["Date"] = receipt_df["Date"].astype(str).str.split(' ').str.get(0)

    payment_df = truncate_df(df.iloc[5:, separation_index+1:terminal_index].reset_index(drop=True))
    payment_df.columns = df.iloc[4, separation_index+1:terminal_index]
    payment_df["Sheet Name"] = sheet_name
    payment_df["Payment Date"] = payment_df["Payment Date"].astype(str).str.split(' ').str.get(0)

    return project_df, receipt_df, payment_df


def prepare_data(data: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    DATA_SHEETS = ["DATA", "GST Computer", "GST", "Summary", "GST Comp", "Design service"]

    project_dfs = []
    receipt_dfs = []
    payment_dfs = []

    for sheet_name in data:
        if sheet_name not in DATA_SHEETS:
            try:
                project_df, receipt_df, payment_df = process_data(sheet_name, data[sheet_name])

                project_df = pd.concat(project_dfs)
                receipt_df = pd.concat(receipt_dfs)
                payment_df = pd.concat(payment_dfs)
            except:
                print(f"Check sheet structure of {sheet_name=}")

            project_dfs.append(project_df)
            receipt_dfs.append(receipt_df)
            payment_dfs.append(payment_df)

    return project_df, receipt_df, payment_df


def main():
    path = Path(__file__).parent / "Data"
    df_map = load_data(path)
    project_df, receipt_df, payment_df = prepare_data(df_map)

    project_path = path / "summary.csv"
    receipt_path = path / "receipt.csv"
    payment_path = path / "payment.csv"

    project_df.to_csv(project_path, index=False)
    receipt_df.to_csv(receipt_path, index=False)
    payment_df.to_csv(payment_path, index=False)


if __name__ == "__main__":
    main()
