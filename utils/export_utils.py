import pandas as pd

def build_excel_report(buffer, in_group_df, ooph_df, nested_df, summary_df, assumptions: dict):
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        in_group_df.to_excel(writer, index=False, sheet_name="In-Group")
        ooph_df.to_excel(writer, index=False, sheet_name="Out-of-Phase")
        nested_df.to_excel(writer, index=False, sheet_name="Nested_Summary")
        summary_df.to_excel(writer, index=False, sheet_name="Group_Summary")
        pd.DataFrame({"Metric": list(assumptions.keys()), "Value": list(assumptions.values())}).to_excel(
            writer, index=False, sheet_name="Assumptions"
        )
    buffer.seek(0)
