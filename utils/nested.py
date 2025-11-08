import pandas as pd

def detect_nested_groups(sorted_centers, eps=0.10):
    """
    sorted_centers: danh sách tâm EFH tăng dần.
    eps: biên ± quanh bội 2 (mặc định 10%)
    Trả về:
      - cent_df: bảng nhóm với cờ nested và 'Nested_In'
      - effective_groups: danh sách tâm nhóm cần thực hiện thực sự (không bị nested vào nhóm lớn hơn)
      - effective_reduction: tỷ lệ giảm số nhóm phải làm
    """
    rows = []
    n = len(sorted_centers)
    nested_flags = [False]*n
    nested_in = [None]*n

    for i, c in enumerate(sorted_centers):
        rows.append({"Group_Index": i+1, "Center_EFH": c})

    for i in range(1, n):
        prev = sorted_centers[i-1]
        curr = sorted_centers[i]
        if prev > 0:
            ratio = curr/prev
            if abs(ratio - 2.0) <= 2.0*eps:  # trong [1.8; 2.2] nếu eps=0.10
                # nhóm i-1 nested vào i
                nested_flags[i-1] = True
                nested_in[i-1] = f"Group-{i+1}"

    cent_df = pd.DataFrame(rows)
    cent_df["Nested_Flag"] = nested_flags
    cent_df["Nested_In"] = nested_in
    cent_df["Group_Label"] = cent_df["Group_Index"].apply(lambda x: f"Group-{x}")

    effective_groups = [sorted_centers[i] for i in range(n) if not nested_flags[i]]
    effective_reduction = 1 - (len(effective_groups) / n) if n > 0 else 0.0
    return cent_df, effective_groups, effective_reduction
