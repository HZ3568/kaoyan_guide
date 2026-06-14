import argparse
import csv
import hashlib
import json
import re
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
WATERMARK_TERMS = [
    "灰灰考研统计",
    "灰灰考研",
    "灰灰",
    "皮皮灰",
    "公众号",
    "后台回复",
    "获取更多资料",
    "资料来源",
    "仅供参考",
    "查询所有专业",
    "领取更新提醒",
]
SUBJECT_FIELDS = ["politics", "english", "math", "professional_course"]
ISSUES_CSV_FIELDS = [
    "图片名",
    "记录序号",
    "学校",
    "学院",
    "专业",
    "问题类型",
    "问题描述",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def make_batch_no() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_output_path(path: Path, overwrite: bool = False) -> Path:
    """
    默认不覆盖已有文件；如目标存在，自动追加序号生成新文件名。
    """
    if overwrite or not path.exists():
        return path

    suffix = path.suffix
    stem = path.stem
    parent = path.parent
    index = 1
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def write_json(path: Path, data: Any, overwrite: bool = False) -> Path:
    output_path = resolve_output_path(path, overwrite=overwrite)
    ensure_dir(output_path.parent)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return output_path


def append_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def ensure_issues_csv(path: Path, overwrite: bool = False) -> None:
    ensure_dir(path.parent)
    if overwrite or not path.exists():
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ISSUES_CSV_FIELDS)
            writer.writeheader()


def append_issues_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ISSUES_CSV_FIELDS)
        if needs_header:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def reset_aggregate_outputs(out_dir: Path) -> None:
    ensure_dir(out_dir)
    for name in ["batch_manifest.jsonl", "records.jsonl"]:
        (out_dir / name).write_text("", encoding="utf-8")
    ensure_issues_csv(out_dir / "issues.csv", overwrite=True)


def ensure_aggregate_outputs(out_dir: Path) -> None:
    ensure_dir(out_dir)
    for name in ["batch_manifest.jsonl", "records.jsonl"]:
        path = out_dir / name
        if not path.exists():
            path.write_text("", encoding="utf-8")
    ensure_issues_csv(out_dir / "issues.csv")


def clean_text(text: str) -> str:
    """
    清洗 OCR 结果
    """
    if not text:
        return ""

    for word in WATERMARK_TERMS:
        text = text.replace(word, "")

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split())

    return text.strip()


def preprocess_image(image_path, out_dir, overwrite: bool = False):

    image_path = Path(image_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(image_path))

    if img is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")

    # 锐化卷积核：必须是 numpy array，不能是普通 list
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    kernel = np.asarray(kernel, dtype=np.float32)

    sharp = cv2.filter2D(img, -1, kernel)

    gray = cv2.cvtColor(sharp, cv2.COLOR_BGR2GRAY)

    processed_path = resolve_output_path(
        out_dir / f"{image_path.stem}_processed.png", overwrite=overwrite
    )
    cv2.imwrite(str(processed_path), gray)

    return processed_path


def merge_positions(positions: List[int], gap: int = 8) -> List[int]:
    """
    将连续或距离很近的线位置合并成一条线。
    """
    if not positions:
        return []

    positions = sorted(positions)
    groups = [[positions[0]]]

    for p in positions[1:]:
        if p - groups[-1][-1] <= gap:
            groups[-1].append(p)
        else:
            groups.append([p])

    return [int(sum(g) / len(g)) for g in groups]


def detect_table_lines(image_path: Path) -> Tuple[List[int], List[int]]:
    """
    检测表格横线和竖线，返回：
    - xs: 竖线 x 坐标列表
    - ys: 横线 y 坐标列表

    原理：
    1. 灰度化
    2. 二值化
    3. 用形态学操作提取横线、竖线
    4. 用投影统计找到线的位置
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 反色二值化：黑色表格线变成白色
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10
    )

    # 横线检测
    horizontal_kernel_len = max(40, w // 30)
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (horizontal_kernel_len, 1)
    )
    horizontal = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1
    )

    # 竖线检测
    vertical_kernel_len = max(30, h // 40)
    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, vertical_kernel_len)
    )
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    # 通过投影找到线位置
    y_projection = horizontal.sum(axis=1)
    x_projection = vertical.sum(axis=0)

    y_threshold = 255 * w * 0.25
    x_threshold = 255 * h * 0.15

    ys = [i for i, value in enumerate(y_projection) if value > y_threshold]
    xs = [i for i, value in enumerate(x_projection) if value > x_threshold]

    ys = merge_positions(ys, gap=10)
    xs = merge_positions(xs, gap=10)

    # 补边界，避免最外侧表格线没检测到
    if not xs or xs[0] > 10:
        xs = [0] + xs
    if xs[-1] < w - 10:
        xs.append(w - 1)

    if not ys or ys[0] > 10:
        ys = [0] + ys
    if ys[-1] < h - 10:
        ys.append(h - 1)

    return xs, ys


def to_python_value(value: Any) -> Any:
    """将 PaddleOCR/numpy 返回值转成普通 Python 对象，便于 JSON 化和解析。"""
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def as_sequence(value: Any) -> List[Any]:
    value = to_python_value(value)
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def first_present(mapping: Mapping[str, Any], keys: List[str]) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def is_flat_box(value: Any) -> bool:
    value = to_python_value(value)
    if not isinstance(value, (list, tuple)) or len(value) < 4:
        return False
    return all(isinstance(x, (int, float, np.integer, np.floating)) for x in value[:4])


def normalize_box(box: Any) -> List[List[float]]:
    box = to_python_value(box)
    if box is None:
        return []

    try:
        arr = np.asarray(box, dtype=np.float32)
    except Exception:
        return []

    if arr.size == 0:
        return []

    if arr.ndim == 1 and arr.size >= 4:
        x1, y1, x2, y2 = arr[:4].tolist()
        return [
            [float(x1), float(y1)],
            [float(x2), float(y1)],
            [float(x2), float(y2)],
            [float(x1), float(y2)],
        ]

    if arr.ndim == 2 and arr.shape[1] >= 2:
        return [[float(p[0]), float(p[1])] for p in arr[:4]]

    return []


def make_ocr_item(text: Any, score: Any, box: Any) -> Dict[str, Any]:
    polygon = normalize_box(box)
    if not polygon:
        return {}

    raw_text_value = "" if text is None else str(text).strip()
    text_value = clean_text(raw_text_value)
    if not text_value:
        return {}

    try:
        score_value = float(score)
    except Exception:
        score_value = 0.0

    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    cx = float(sum(xs) / len(xs))
    cy = float(sum(ys) / len(ys))

    return {
        "text": text_value,
        "raw_text": raw_text_value,
        "score": score_value,
        "box": polygon,
        "cx": cx,
        "cy": cy,
    }


def paddle_result_mapping(result_part: Any) -> Dict[str, Any]:
    if isinstance(result_part, Mapping):
        if isinstance(result_part.get("res"), Mapping):
            return dict(result_part["res"])
        return dict(result_part)

    if hasattr(result_part, "keys"):
        try:
            result_dict = {key: result_part[key] for key in result_part.keys()}
            if isinstance(result_dict.get("res"), Mapping):
                return dict(result_dict["res"])
            return result_dict
        except Exception:
            pass

    json_value = getattr(result_part, "json", None)
    if callable(json_value):
        json_value = json_value()

    if isinstance(json_value, Mapping):
        if isinstance(json_value.get("res"), Mapping):
            return dict(json_value["res"])
        return dict(json_value)

    return {}


def parse_paddleocr_3x_result(result: Any) -> List[Dict[str, Any]]:
    pages = result if isinstance(result, list) else [result]
    items: List[Dict[str, Any]] = []

    for page in pages:
        page_data = paddle_result_mapping(page)
        if not page_data:
            continue

        texts = as_sequence(first_present(page_data, ["rec_texts", "texts"]))
        scores = as_sequence(first_present(page_data, ["rec_scores", "scores"]))
        boxes_value = first_present(
            page_data, ["rec_polys", "rec_boxes", "dt_polys", "boxes"]
        )
        boxes = as_sequence(boxes_value)

        for idx, text in enumerate(texts):
            score = scores[idx] if idx < len(scores) else 0.0
            if len(texts) == 1 and is_flat_box(boxes):
                box = boxes
            else:
                box = boxes[idx] if idx < len(boxes) else None

            item = make_ocr_item(text, score, box)
            if item:
                items.append(item)

    return items


def parse_legacy_paddleocr_result(result: Any) -> List[Dict[str, Any]]:
    if not result:
        return []

    pages = result
    if not (
        isinstance(result, list)
        and len(result) > 0
        and isinstance(result[0], (list, tuple))
    ):
        pages = [result]

    items: List[Dict[str, Any]] = []

    for page in pages:
        if not isinstance(page, (list, tuple)):
            continue

        for line in page:
            if not isinstance(line, (list, tuple)) or len(line) < 2:
                continue

            text_info = line[1]
            if not isinstance(text_info, (list, tuple)) or len(text_info) < 2:
                continue

            item = make_ocr_item(text_info[0], text_info[1], line[0])
            if item:
                items.append(item)

    return items


def debug_paddleocr_result(result: Any, items: List[Dict[str, Any]]) -> None:
    print(f"    OCR 返回结果类型: {type(result)}")

    first_result = result[0] if isinstance(result, list) and result else result
    result_mapping = paddle_result_mapping(first_result)
    keys = list(result_mapping.keys())
    print(f"    OCR 字段 keys: {keys}")

    preview_texts = [item["text"] for item in items[:5]]
    if not preview_texts:
        preview_texts = [
            clean_text(str(text))
            for text in as_sequence(
                first_present(result_mapping, ["rec_texts", "texts"])
            )[:5]
        ]
    print(f"    OCR 前5条文本: {preview_texts}")


_PADDLE_OCR = None


def get_paddleocr_engine():
    global _PADDLE_OCR
    if _PADDLE_OCR is not None:
        return _PADDLE_OCR

    import os

    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["PADDLE_DEVICE"] = "cpu"
    from paddleocr import PaddleOCR

    try:
        import paddle

        paddle.set_device("cpu")
    except Exception:
        pass

    _PADDLE_OCR = PaddleOCR(
        lang="ch",
        device="cpu",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    return _PADDLE_OCR


def run_paddleocr(image_path: Path) -> List[Dict[str, Any]]:
    """
    调用 PaddleOCR 识别图片。
    输出每个文本块：
    {
        "text": "...",
        "score": 0.98,
        "box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],
        "cx": 中心点x,
        "cy": 中心点y
    }
    """
    ocr = get_paddleocr_engine()

    if hasattr(ocr, "predict"):
        result = ocr.predict(str(image_path))
    else:
        result = ocr.ocr(str(image_path), cls=False)

    items = parse_paddleocr_3x_result(result)
    if not items:
        items = parse_legacy_paddleocr_result(result)

    debug_paddleocr_result(result, items)
    return items


def find_interval(value: float, lines: List[int]) -> int:
    """
    找到 value 落在哪两个表格线之间。
    """
    for i in range(len(lines) - 1):
        if lines[i] <= value < lines[i + 1]:
            return i
    return -1


def build_cell_matrix(
    ocr_items: List[Dict[str, Any]],
    xs: List[int],
    ys: List[int],
    text_key: str = "text",
    do_clean: bool = True,
) -> List[List[str]]:
    """
    根据 OCR 文本坐标，把文字放回表格单元格。
    """
    rows = len(ys) - 1
    cols = len(xs) - 1

    cells: List[List[List[Dict[str, Any]]]] = [
        [[] for _ in range(cols)] for _ in range(rows)
    ]

    for item in ocr_items:
        col = find_interval(item["cx"], xs)
        row = find_interval(item["cy"], ys)

        if row >= 0 and col >= 0:
            cells[row][col].append(item)

    matrix: List[List[str]] = []

    for r in range(rows):
        row_values = []
        for c in range(cols):
            parts = sorted(cells[r][c], key=lambda x: (x["cy"], x["cx"]))
            text = " ".join([str(p.get(text_key, "")) for p in parts])
            row_values.append(clean_text(text) if do_clean else " ".join(text.split()))
        matrix.append(row_values)

    return matrix


def extract_school_info(ocr_items: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    从图片顶部标题中抽取学校名称和学校代码。
    """
    # 只看图片上方 15% 的文本
    if not ocr_items:
        return {"school": "", "school_code": ""}

    max_y = max(item["cy"] for item in ocr_items)
    top_items = [x for x in ocr_items if x["cy"] < max_y * 0.18]
    top_text = " ".join(
        [x["text"] for x in sorted(top_items, key=lambda v: (v["cy"], v["cx"]))]
    )
    top_text = clean_text(top_text)

    code_match = re.search(r"\b(\d{5})\b", top_text)
    school_code = code_match.group(1) if code_match else ""

    school = ""
    school_match = re.search(r"([\u4e00-\u9fa5]{2,20}大学)", top_text)
    if school_match:
        school = school_match.group(1)

    return {"school": school, "school_code": school_code}


def clean_college_name(text: str) -> str:
    """
    清洗学院标题。
    例如：
    105计算机科学与工程学院-人工智能学院-皮皮灰
    -> 计算机科学与工程学院-人工智能学院
    """
    text = clean_text(text)
    text = re.sub(r"^\d+", "", text)
    text = re.sub(r"[-—]?(皮皮灰|灰灰考研|灰灰).*?$", "", text)
    text = text.replace("、", "-")
    return text.strip(" -—")


def is_college_row(row_text: str) -> bool:
    """
    判断一行是否是学院标题行。
    """
    if "学院" not in row_text:
        return False

    blacklist = ["院校文章", "后台回复", "院校信息", "复试相关", "免责声明"]
    if any(x in row_text for x in blacklist):
        return False

    # 学院标题一般不会特别长
    return len(row_text) <= 80


def is_major_name(text: str) -> bool:
    """
    判断单元格内容是否像专业名称。
    """
    if not text:
        return False

    blacklist = [
        "专业名称",
        "复试相关",
        "免责声明",
        "公众号",
        "后台回复",
        "初试科目",
        "分数线",
        "复试人数",
        "预计招生人数",
    ]
    if any(x in text for x in blacklist):
        return False

    # 常见专业/方向关键词
    keywords = [
        "计算机",
        "软件工程",
        "电子信息",
        "人工智能",
        "大数据",
        "网安",
        "网络安全",
        "生物医学",
        "技术",
    ]
    return any(k in text for k in keywords)


def extract_int(text: str) -> str:
    """
    从文本中抽取数字。
    用字符串返回，避免 OCR 错误时强转失败。
    """
    if not text:
        return ""

    nums = re.findall(r"\d+", text)
    if not nums:
        return ""

    return nums[0]


def extract_major_records(
    matrix: List[List[str]],
    school_info: Dict[str, str],
    source_file: str,
    raw_matrix: Optional[List[List[str]]] = None,
) -> List[Dict[str, Any]]:
    """
    从单元格矩阵中抽取专业记录。

    注意：
    这类第三方统计图可能存在合并单元格。
    自动解析后仍然建议人工检查 expected_enrollment、复试科目等关键字段。
    """
    records: List[Dict[str, Any]] = []

    current_college = ""

    for row_index, row in enumerate(matrix):
        row_text = clean_text(" ".join([x for x in row if x]))
        raw_row = raw_matrix[row_index] if raw_matrix and row_index < len(raw_matrix) else row

        if not row_text:
            continue

        # 学院标题行
        if is_college_row(row_text):
            current_college = clean_college_name(row_text)
            continue

        # 至少要有 5 列：专业、政治、英语、数学、专业课
        if len(row) < 5:
            continue

        major = clean_text(row[0])

        if not is_major_name(major):
            continue

        politics = clean_text(row[1]) if len(row) > 1 else ""
        english = clean_text(row[2]) if len(row) > 2 else ""
        math = clean_text(row[3]) if len(row) > 3 else ""
        professional_course = clean_text(row[4]) if len(row) > 4 else ""

        score_line = clean_text(row[5]) if len(row) > 5 else ""
        re_exam_count = clean_text(row[6]) if len(row) > 6 else ""
        re_exam_total_avg = clean_text(row[7]) if len(row) > 7 else ""
        re_exam_subject_avg = clean_text(row[8]) if len(row) > 8 else ""
        expected_enrollment = extract_int(row[9]) if len(row) > 9 else ""
        admission_score = clean_text(row[10]) if len(row) > 10 else ""

        record = {
            "school": school_info.get("school", ""),
            "school_code": school_info.get("school_code", ""),
            "college": current_college,
            "major": major,
            "politics": politics,
            "english": english,
            "math": math,
            "professional_course": professional_course,
            "score_line": score_line,
            "re_exam_count": re_exam_count,
            "re_exam_total_avg": re_exam_total_avg,
            "re_exam_subject_avg": re_exam_subject_avg,
            "expected_enrollment": expected_enrollment,
            "admission_score": admission_score,
            "source_type": "image_ocr",
            "source_file": source_file,
            "source_reliability": "third_party",
            "need_official_check": True,
            "verified": False,
            "_raw_initial_subjects": [
                raw_row[1] if len(raw_row) > 1 else "",
                raw_row[2] if len(raw_row) > 2 else "",
                raw_row[3] if len(raw_row) > 3 else "",
                raw_row[4] if len(raw_row) > 4 else "",
            ],
        }

        records.append(record)

    return records


def add_issue(
    issues: List[Dict[str, str]], issue_type: str, field: str, description: str
) -> None:
    issues.append(
        {
            "type": issue_type,
            "field": field,
            "description": description,
        }
    )


def contains_watermark(text: str) -> bool:
    if not text:
        return False
    compact = re.sub(r"\s+", "", text)
    return any(term in compact for term in WATERMARK_TERMS)


def has_valid_score(text: str) -> bool:
    if not text:
        return False
    nums = [int(x) for x in re.findall(r"\d+", text)]
    return any(100 <= x <= 500 for x in nums)


def is_numeric_text(text: str) -> bool:
    if not text:
        return False
    return bool(re.fullmatch(r"\d+", str(text).strip()))


def looks_like_score_or_count(text: str) -> bool:
    if not text:
        return False
    text = str(text)
    if re.fullmatch(r"\d+", text.strip()):
        return True
    suspicious_keywords = [
        "复试最低",
        "分数线",
        "拟录取",
        "第",
        "平均",
        "均分",
        "招生人数",
    ]
    return any(keyword in text for keyword in suspicious_keywords)


def validate_subject_alignment(record: Dict[str, Any], issues: List[Dict[str, str]]) -> None:
    politics = record.get("politics", "")
    english = record.get("english", "")
    math = record.get("math", "")
    professional_course = record.get("professional_course", "")

    if politics and ("英语" in politics or "数学" in politics or looks_like_score_or_count(politics)):
        add_issue(
            issues,
            "字段明显错位",
            "politics",
            f"政治字段疑似混入其他科目或分数字段：{politics}",
        )
    if english and ("数学" in english or looks_like_score_or_count(english)):
        add_issue(
            issues,
            "字段明显错位",
            "english",
            f"英语字段疑似混入数学或分数字段：{english}",
        )
    if math and ("复试" in math or "分数" in math or looks_like_score_or_count(math)):
        add_issue(
            issues,
            "字段明显错位",
            "math",
            f"数学字段疑似混入分数线或复试字段：{math}",
        )
    if professional_course and looks_like_score_or_count(professional_course):
        add_issue(
            issues,
            "字段明显错位",
            "professional_course",
            f"专业课字段疑似混入分数或人数：{professional_course}",
        )


def validate_record(record: Dict[str, Any]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []

    if not record.get("school_code"):
        add_issue(issues, "学校代码为空", "school_code", "未能从图片标题中识别学校代码")

    if not record.get("school"):
        add_issue(issues, "学校名称为空", "school", "未能从图片标题中识别学校名称")

    if not record.get("major"):
        add_issue(issues, "专业名称为空", "major", "专业名称为空")

    score_line = record.get("score_line", "")
    if not score_line:
        add_issue(issues, "分数线格式异常", "score_line", "分数线字段为空")
    elif not has_valid_score(score_line):
        add_issue(
            issues,
            "分数线格式异常",
            "score_line",
            f"分数线字段未识别到 100-500 范围内的有效分数：{score_line}",
        )

    expected_enrollment = record.get("expected_enrollment", "")
    if not is_numeric_text(expected_enrollment):
        add_issue(
            issues,
            "招生人数不是数字",
            "expected_enrollment",
            f"预计招生人数不是纯数字：{expected_enrollment or '空'}",
        )

    raw_subjects = record.get("_raw_initial_subjects", [])
    subject_values = [record.get(field, "") for field in SUBJECT_FIELDS]
    for field, value in zip(SUBJECT_FIELDS, subject_values):
        if contains_watermark(value):
            add_issue(
                issues,
                "初试科目包含水印词",
                field,
                f"初试科目字段包含水印或推广词：{value}",
            )
    for raw_value in raw_subjects:
        if contains_watermark(raw_value):
            add_issue(
                issues,
                "初试科目包含水印词",
                "initial_subjects_raw",
                f"初试科目原始 OCR 文本包含水印或推广词：{raw_value}",
            )

    validate_subject_alignment(record, issues)

    return issues


def calculate_confidence(issues: List[Dict[str, str]]) -> float:
    score = 1.0
    weights = {
        "学校代码为空": 0.12,
        "学校名称为空": 0.15,
        "专业名称为空": 0.25,
        "分数线格式异常": 0.15,
        "招生人数不是数字": 0.1,
        "初试科目包含水印词": 0.12,
        "字段明显错位": 0.18,
    }
    for issue in issues:
        score -= weights.get(issue.get("type", ""), 0.08)
    return round(max(0.0, score), 3)


def enrich_records(
    records: List[Dict[str, Any]], image_path: Path, file_hash: str, batch_no: str
) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        record["record_seq"] = index
        record["source_image"] = image_path.name
        record["file_hash"] = file_hash
        record["batch_no"] = batch_no
        issues = validate_record(record)
        record["issues"] = issues
        record["confidence"] = calculate_confidence(issues)
        record.pop("_raw_initial_subjects", None)
        enriched.append(record)
    return enriched


def build_issue_rows(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for record in records:
        for issue in record.get("issues", []):
            rows.append(
                {
                    "图片名": record.get("source_image", ""),
                    "记录序号": record.get("record_seq", ""),
                    "学校": record.get("school", ""),
                    "学院": record.get("college", ""),
                    "专业": record.get("major", ""),
                    "问题类型": issue.get("type", ""),
                    "问题描述": issue.get("description", ""),
                }
            )
    return rows


def make_rag_chunk(record: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """
    将结构化专业记录转成适合向量检索的自然语言 chunk。
    """
    school = record.get("school", "")
    school_code = record.get("school_code", "")
    college = record.get("college", "")
    major = record.get("major", "")

    subjects = [
        record.get("politics", ""),
        record.get("english", ""),
        record.get("math", ""),
        record.get("professional_course", ""),
    ]
    subjects = [x for x in subjects if x]

    content_parts = []

    base = f"{school}{school_code}，{college}的{major}专业"
    if subjects:
        base += f"，初试科目包括{'、'.join(subjects)}"
    if record.get("expected_enrollment"):
        base += f"，预计招生人数为{record['expected_enrollment']}人"
    if record.get("score_line"):
        base += f"，分数线信息为{record['score_line']}"
    if record.get("admission_score"):
        base += f"，拟录取分数信息为{record['admission_score']}"

    base += (
        "。该信息来源于第三方考研统计图片，具体招生信息应以学校研究生院官网公布为准。"
    )
    content_parts.append(base)

    content = clean_text("".join(content_parts))

    chunk_id = f"{record.get('school_code', 'unknown')}_{idx:04d}"

    return {
        "chunk_id": chunk_id,
        "doc_id": f"{record.get('school_code', 'unknown')}_image_ocr",
        "school": school,
        "school_code": school_code,
        "college": college,
        "major": major,
        "category": "考研招生统计",
        "source_type": "image_ocr",
        "source_file": record.get("source_file", ""),
        "source_reliability": record.get("source_reliability", "third_party"),
        "need_official_check": True,
        "verified": record.get("verified", False),
        "content": content,
    }


def write_jsonl(path: Path, rows: List[Dict[str, Any]], overwrite: bool = False) -> Path:
    output_path = resolve_output_path(path, overwrite=overwrite)
    ensure_dir(output_path.parent)
    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return output_path


def write_cell_matrix(path: Path, matrix: List[List[str]], overwrite: bool = False) -> Path:
    output_path = resolve_output_path(path, overwrite=overwrite)
    ensure_dir(output_path.parent)
    pd.DataFrame(matrix).to_csv(
        output_path, index=False, header=False, encoding="utf-8-sig"
    )
    return output_path


def image_output_dir(out_dir: Path, image_path: Path) -> Path:
    safe_stem = re.sub(r"[^\w\u4e00-\u9fa5.-]+", "_", image_path.stem).strip("_")
    if not safe_stem:
        safe_stem = "image"
    return out_dir / safe_stem


def process_image(
    image_path: Path,
    out_dir: Path,
    batch_no: str,
    overwrite: bool = False,
    batch_mode: bool = False,
    write_legacy_outputs: bool = False,
) -> Dict[str, Any]:
    image_path = Path(image_path)
    out_dir = Path(out_dir)
    file_hash = file_sha256(image_path)
    per_image_dir = image_output_dir(out_dir, image_path) if batch_mode else out_dir
    ensure_dir(per_image_dir)

    print(f"[1] 预处理图片: {image_path}")
    processed_path = preprocess_image(image_path, per_image_dir, overwrite=overwrite)

    print(f"[2] 检测表格线: {processed_path}")
    xs, ys = detect_table_lines(processed_path)

    print(f"    检测到竖线数量: {len(xs)}")
    print(f"    检测到横线数量: {len(ys)}")

    print(f"[3] 执行 PaddleOCR: {image_path}")
    ocr_items = run_paddleocr(image_path)
    print(f"    OCR 文本块数量: {len(ocr_items)}")

    raw_ocr_name = "raw_ocr.json" if batch_mode else f"{image_path.stem}_ocr_items.json"
    raw_ocr_path = write_json(per_image_dir / raw_ocr_name, ocr_items, overwrite=overwrite)

    print("[4] 构建单元格矩阵")
    matrix = build_cell_matrix(ocr_items, xs, ys)
    raw_matrix = build_cell_matrix(
        ocr_items, xs, ys, text_key="raw_text", do_clean=False
    )

    cell_matrix_name = "cell_matrix.csv" if batch_mode else f"{image_path.stem}_cells.csv"
    cells_csv_path = write_cell_matrix(
        per_image_dir / cell_matrix_name, matrix, overwrite=overwrite
    )

    print("[5] 抽取学校信息")
    school_info = extract_school_info(ocr_items)
    print(f"    school_info = {school_info}")

    print("[6] 抽取专业记录")
    records = extract_major_records(
        matrix=matrix,
        school_info=school_info,
        source_file=str(image_path),
        raw_matrix=raw_matrix,
    )
    records = enrich_records(records, image_path, file_hash, batch_no)
    issue_rows = build_issue_rows(records)

    print(f"    抽取专业记录数量: {len(records)}")
    print(f"    质量问题数量: {len(issue_rows)}")

    legacy_major_records_path = None
    legacy_chunks_path = None
    if write_legacy_outputs:
        cleaned_dir = Path("data/cleaned")
        chunks_dir = Path("data/chunks")
        ensure_dir(cleaned_dir)
        ensure_dir(chunks_dir)

        legacy_major_records_path = write_jsonl(
            cleaned_dir / f"{image_path.stem}_major_records.jsonl",
            records,
            overwrite=overwrite,
        )

        print("[7] 生成 RAG chunks")
        chunks = [make_rag_chunk(record, i + 1) for i, record in enumerate(records)]
        legacy_chunks_path = write_jsonl(
            chunks_dir / f"{image_path.stem}_chunks.jsonl",
            chunks,
            overwrite=overwrite,
        )

    return {
        "image_path": str(image_path),
        "source_image": image_path.name,
        "file_hash": file_hash,
        "batch_no": batch_no,
        "status": "processed",
        "raw_ocr_path": str(raw_ocr_path),
        "cell_matrix_path": str(cells_csv_path),
        "processed_image_path": str(processed_path),
        "record_count": len(records),
        "issue_count": len(issue_rows),
        "records": records,
        "issue_rows": issue_rows,
        "legacy_major_records_path": str(legacy_major_records_path)
        if legacy_major_records_path
        else "",
        "legacy_chunks_path": str(legacy_chunks_path) if legacy_chunks_path else "",
    }


def discover_images(input_dir: Path) -> List[Path]:
    input_dir = Path(input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")
    return sorted(
        [
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ]
    )


def load_processed_hashes(manifest_path: Path) -> set[str]:
    if not manifest_path.exists():
        return set()

    hashes: set[str] = set()
    with manifest_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("status") == "processed" and row.get("file_hash"):
                hashes.add(str(row["file_hash"]))
    return hashes


def manifest_row_from_result(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "batch_no": result.get("batch_no", ""),
        "image_path": result.get("image_path", ""),
        "source_image": result.get("source_image", ""),
        "file_hash": result.get("file_hash", ""),
        "status": result.get("status", ""),
        "record_count": result.get("record_count", 0),
        "issue_count": result.get("issue_count", 0),
        "raw_ocr_path": result.get("raw_ocr_path", ""),
        "cell_matrix_path": result.get("cell_matrix_path", ""),
        "processed_image_path": result.get("processed_image_path", ""),
        "error_message": result.get("error_message", ""),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def write_batch_outputs(
    out_dir: Path,
    result: Dict[str, Any],
    overwrite_aggregate: bool = False,
) -> None:
    manifest_path = out_dir / "batch_manifest.jsonl"
    records_path = out_dir / "records.jsonl"
    issues_path = out_dir / "issues.csv"

    append_jsonl(manifest_path, [manifest_row_from_result(result)])
    append_jsonl(records_path, result.get("records", []))
    ensure_issues_csv(issues_path, overwrite=overwrite_aggregate)
    append_issues_csv(issues_path, result.get("issue_rows", []))


def run_single(args: argparse.Namespace) -> None:
    image_path = Path(args.image)
    out_dir = Path(args.out)
    ensure_dir(out_dir)
    if args.overwrite:
        reset_aggregate_outputs(out_dir)
    else:
        ensure_aggregate_outputs(out_dir)

    batch_no = args.batch_no or f"single_{make_batch_no()}"
    file_hash = file_sha256(image_path)
    manifest_path = out_dir / "batch_manifest.jsonl"
    if not args.overwrite and file_hash in load_processed_hashes(manifest_path):
        result = {
            "image_path": str(image_path),
            "source_image": image_path.name,
            "file_hash": file_hash,
            "batch_no": batch_no,
            "status": "skipped_duplicate",
            "record_count": 0,
            "issue_count": 0,
            "error_message": "文件 hash 已处理，跳过重复图片",
        }
        append_jsonl(manifest_path, [manifest_row_from_result(result)])
        print(f"已跳过重复图片: {image_path}")
        print(f"  批处理清单:   {manifest_path}")
        return

    result = process_image(
        image_path=image_path,
        out_dir=out_dir,
        batch_no=batch_no,
        overwrite=args.overwrite,
        batch_mode=False,
        write_legacy_outputs=True,
    )
    write_batch_outputs(out_dir, result, overwrite_aggregate=False)

    print("\n处理完成：")
    print(f"  batch_no:     {batch_no}")
    print(f"  OCR 原始结果: {result['raw_ocr_path']}")
    print(f"  单元格 CSV:   {result['cell_matrix_path']}")
    print(f"  专业结构化:   {result['legacy_major_records_path']}")
    print(f"  RAG chunks:  {result['legacy_chunks_path']}")
    print(f"  批处理清单:   {out_dir / 'batch_manifest.jsonl'}")
    print(f"  汇总记录:     {out_dir / 'records.jsonl'}")
    print(f"  问题报告:     {out_dir / 'issues.csv'}")


def run_batch(args: argparse.Namespace) -> None:
    input_dir = Path(args.input_dir)
    out_dir = Path(args.out)
    ensure_dir(out_dir)
    if args.overwrite:
        reset_aggregate_outputs(out_dir)
    else:
        ensure_aggregate_outputs(out_dir)

    batch_no = args.batch_no or f"batch_{make_batch_no()}"
    manifest_path = out_dir / "batch_manifest.jsonl"
    processed_hashes = set() if args.overwrite else load_processed_hashes(manifest_path)
    current_hashes: set[str] = set()
    images = discover_images(input_dir)

    print(f"批处理开始：batch_no={batch_no}, 图片数量={len(images)}")

    processed_count = 0
    skipped_count = 0
    failed_count = 0

    for image_path in images:
        file_hash = file_sha256(image_path)
        if not args.overwrite and (file_hash in processed_hashes or file_hash in current_hashes):
            skipped_count += 1
            result = {
                "image_path": str(image_path),
                "source_image": image_path.name,
                "file_hash": file_hash,
                "batch_no": batch_no,
                "status": "skipped_duplicate",
                "record_count": 0,
                "issue_count": 0,
                "error_message": "文件 hash 已处理，跳过重复图片",
            }
            append_jsonl(manifest_path, [manifest_row_from_result(result)])
            print(f"[跳过] {image_path.name}: hash 已处理")
            continue

        current_hashes.add(file_hash)
        try:
            result = process_image(
                image_path=image_path,
                out_dir=out_dir,
                batch_no=batch_no,
                overwrite=args.overwrite,
                batch_mode=True,
                write_legacy_outputs=False,
            )
            write_batch_outputs(out_dir, result, overwrite_aggregate=False)
            processed_count += 1
        except Exception as e:
            failed_count += 1
            result = {
                "image_path": str(image_path),
                "source_image": image_path.name,
                "file_hash": file_hash,
                "batch_no": batch_no,
                "status": "failed",
                "record_count": 0,
                "issue_count": 0,
                "error_message": str(e),
            }
            append_jsonl(manifest_path, [manifest_row_from_result(result)])
            print(f"[失败] {image_path.name}: {e}")

    print("\n批处理完成：")
    print(f"  batch_no:   {batch_no}")
    print(f"  已处理:     {processed_count}")
    print(f"  已跳过重复: {skipped_count}")
    print(f"  失败:       {failed_count}")
    print(f"  批处理清单: {out_dir / 'batch_manifest.jsonl'}")
    print(f"  汇总记录:   {out_dir / 'records.jsonl'}")
    print(f"  问题报告:   {out_dir / 'issues.csv'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="输入单张图片路径")
    parser.add_argument("--input-dir", default="data/raw/images", help="批处理图片目录")
    parser.add_argument("--out", default="data/extracted/ocr", help="输出目录")
    parser.add_argument("--batch", action="store_true", help="启用批量处理模式")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已有输出文件")
    parser.add_argument("--batch-no", help="手动指定批次号")
    args = parser.parse_args()

    if args.batch:
        run_batch(args)
        return

    if not args.image:
        parser.error("非批处理模式必须提供 --image")
    run_single(args)


if __name__ == "__main__":
    main()
