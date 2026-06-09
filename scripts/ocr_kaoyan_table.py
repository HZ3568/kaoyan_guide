import argparse
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import pandas as pd


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clean_text(text: str) -> str:
    """
    清洗 OCR 结果
    """
    if not text:
        return ""

    remove_words = [
        "灰灰考研统计",
        "灰灰考研",
        "公众号",
        "后台回复",
        "获取更多资料",
        "仅供参考",
    ]

    for word in remove_words:
        text = text.replace(word, "")

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split())

    return text.strip()


def preprocess_image(image_path, out_dir):

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

    processed_path = out_dir / f"{image_path.stem}_processed.png"
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

    text_value = clean_text(str(text))
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
    import os

    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["PADDLE_DEVICE"] = "cpu"
    from paddleocr import PaddleOCR

    try:
        import paddle

        paddle.set_device("cpu")
    except Exception:
        pass

    ocr = PaddleOCR(
        lang="ch",
        device="cpu",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

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
    ocr_items: List[Dict[str, Any]], xs: List[int], ys: List[int]
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
            text = " ".join([p["text"] for p in parts])
            row_values.append(clean_text(text))
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
    matrix: List[List[str]], school_info: Dict[str, str], source_file: str
) -> List[Dict[str, Any]]:
    """
    从单元格矩阵中抽取专业记录。

    注意：
    这类第三方统计图可能存在合并单元格。
    自动解析后仍然建议人工检查 expected_enrollment、复试科目等关键字段。
    """
    records: List[Dict[str, Any]] = []

    current_college = ""

    for row in matrix:
        row_text = clean_text(" ".join([x for x in row if x]))

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
        }

        records.append(record)

    return records


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


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="输入图片路径")
    parser.add_argument("--out", default="data/extracted/ocr", help="输出目录")
    args = parser.parse_args()

    image_path = Path(args.image)
    out_dir = Path(args.out)

    ensure_dir(out_dir)

    print(f"[1] 预处理图片: {image_path}")
    processed_path = preprocess_image(image_path, out_dir)

    print(f"[2] 检测表格线: {processed_path}")
    xs, ys = detect_table_lines(processed_path)

    print(f"    检测到竖线数量: {len(xs)}")
    print(f"    检测到横线数量: {len(ys)}")

    print(f"[3] 执行 PaddleOCR: {image_path}")
    ocr_items = run_paddleocr(image_path)

    print(f"    OCR 文本块数量: {len(ocr_items)}")

    # 保存 OCR 原始结果
    raw_ocr_path = out_dir / f"{image_path.stem}_ocr_items.json"
    with raw_ocr_path.open("w", encoding="utf-8") as f:
        json.dump(ocr_items, f, ensure_ascii=False, indent=2)

    print("[4] 构建单元格矩阵")
    matrix = build_cell_matrix(ocr_items, xs, ys)

    # 保存为 CSV，方便人工检查
    cells_csv_path = out_dir / f"{image_path.stem}_cells.csv"
    pd.DataFrame(matrix).to_csv(
        cells_csv_path, index=False, header=False, encoding="utf-8-sig"
    )

    print("[5] 抽取学校信息")
    school_info = extract_school_info(ocr_items)
    print(f"    school_info = {school_info}")

    print("[6] 抽取专业记录")
    records = extract_major_records(
        matrix=matrix, school_info=school_info, source_file=str(image_path)
    )

    print(f"    抽取专业记录数量: {len(records)}")

    cleaned_dir = Path("data/cleaned")
    chunks_dir = Path("data/chunks")
    ensure_dir(cleaned_dir)
    ensure_dir(chunks_dir)

    major_records_path = cleaned_dir / f"{image_path.stem}_major_records.jsonl"
    write_jsonl(major_records_path, records)

    print("[7] 生成 RAG chunks")
    chunks = [make_rag_chunk(record, i + 1) for i, record in enumerate(records)]

    chunks_path = chunks_dir / f"{image_path.stem}_chunks.jsonl"
    write_jsonl(chunks_path, chunks)

    print("\n处理完成：")
    print(f"  OCR 原始结果: {raw_ocr_path}")
    print(f"  单元格 CSV:   {cells_csv_path}")
    print(f"  专业结构化:   {major_records_path}")
    print(f"  RAG chunks:  {chunks_path}")


if __name__ == "__main__":
    main()
