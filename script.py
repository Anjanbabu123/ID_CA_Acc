from pathlib import Path
import warnings

import pandas as pd


warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def load_data(path: Path) -> dict[str, pd.DataFrame]:
    FILE_NAME = "P&L 20-21-22.xlsx"

    data_path = path / FILE_NAME

    print(f"Loading data from {data_path!s}")

    return pd.read_excel(data_path, sheet_name=None, header=None)


def truncate_df(df: pd.DataFrame) -> pd.DataFrame:
    threshold = df.shape[1] // 2
    return df.dropna(axis=0, how="any", thresh=threshold).reset_index(drop=True)


def process_data(sheet_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start_index = None
    terminal_index = None
    start_index2 = None
    terminal_index2 = None

    for idx, header in enumerate(df.iloc[1].values):
        if start_index is None and not pd.isnull(header):
            start_index = idx
            continue
        if terminal_index is None and pd.isnull(header):
            terminal_index = idx
            continue
        if terminal_index is not None and start_index2 is None and not pd.isnull(header):
            start_index2 = idx
            continue
        if terminal_index is not None and start_index2 is not None and terminal_index2 is None and pd.isnull(header):
            terminal_index2 = idx
            continue

    project_df_1 = df.iloc[2:3, start_index:terminal_index].reset_index(drop=True)
    project_df_1.columns = df.iloc[1, start_index:terminal_index]

    project_df_2 = df.iloc[2:3, start_index2:terminal_index2].reset_index(drop=True)
    project_df_2.columns = df.iloc[1, start_index2:terminal_index2]

    project_df = pd.concat([project_df_1, project_df_2], axis=1)

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
    DATA_SHEETS = ["DATA", "GST Computer", "GST", "Summary", "GST Comp", "Design service",
                   "Project List", "Sheet46", "P&L Summary", "HO Summary", "Design service"]

    project_dfs = []
    receipt_dfs = []
    payment_dfs = []

    for sheet_name in data:
        if sheet_name not in DATA_SHEETS:
            try:
                project_df, receipt_df, payment_df = process_data(sheet_name, data[sheet_name])
                project_dfs.append(project_df)
                receipt_dfs.append(receipt_df)
                payment_dfs.append(payment_df)
            except Exception as exc:
                print(exc)
                print(f"{sheet_name=} CHECK SHEET STRUCTURE")

    project_df = pd.concat(project_dfs)
    receipt_df = pd.concat(receipt_dfs)
    payment_df = pd.concat(payment_dfs)

    return project_df, receipt_df, payment_df


def main():
    path = Path(__file__).parent / "Data"

    print("Loading data")
    df_map = load_data(path)

    print("Preparing data")
    project_df, receipt_df, payment_df = prepare_data(df_map)

    project_path = path / "summary.csv"
    receipt_path = path / "receipt.csv"
    payment_path = path / "payment.csv"

    print("Writing data")
    print("|-- Project summary")
    project_df.to_csv(project_path, index=False)
    print("|-- Receipts")
    receipt_df.to_csv(receipt_path, index=False)
    print("|-- Payments")
    payment_df.to_csv(payment_path, index=False)


if __name__ == "__main__":
    main()