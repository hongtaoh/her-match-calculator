import streamlit as st
import pandas as pd
import json

@st.cache_data 
def load_data():
    data = pd.read_parquet("data/data_numeric.parquet")
    with open('data/mappings.json', "r", encoding="utf-8") as f:
        mappings = json.load(f)
    return data, mappings

# 在加载数据后立即计算
data, mappings = load_data()

# 设置页面样式
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 2rem;
            color: #333;
            text-align: center;
            padding: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-header">中国女性择偶指南</h1>', unsafe_allow_html=True)

st.sidebar.header("筛选")

# 用户输入筛选条件
age = st.sidebar.slider("年龄范围", min_value=18, max_value=60, value=(18, 60))
height = st.sidebar.slider("身高范围 (cm)", min_value=150, max_value=200, value=(150, 200))

# 定义正确的选项顺序
education_order = ["初中及以下", "高中", "大专", "本科", "研究生", "博士"]
family_asset_order = ["<10万", "10-50万", "50-100万", "100-500万", ">500万"]
personal_income_order = ["<10万", "10-50万", "50-100万", "100-500万", ">500万"]
location_order = ["一线城市", "二线城市", "县城", "农村"]

# 最低要求选项
education = st.sidebar.selectbox("最低学历", options=education_order, index=0)
family_asset = st.sidebar.selectbox("最低家庭资产", options=family_asset_order, index=0)
personal_income = st.sidebar.selectbox("最低个人年收入", options=personal_income_order, index=0)

# 评分选项
min_face_score = st.sidebar.slider("最低颜值评分", min_value=1, max_value=4, value=1)
min_humor_score = st.sidebar.slider("最低幽默评分", min_value=1, max_value=4, value=1)
min_sex_attract_score = st.sidebar.slider("最低性吸引力评分", min_value=1, max_value=4, value=1)
min_body_score = st.sidebar.slider("最低身材评分", min_value=1, max_value=4, value=1)

# 单选选项
health_status = st.sidebar.radio("健康状况", options=["无所谓"] + list(mappings["health_status"].keys()), index=0)
religion = st.sidebar.radio("宗教信仰", options=["无所谓"] + list(mappings["religion"].keys()), index=0)

# 创建改进的多选框
def create_checkbox_select(label, options_dict, custom_order=None):
    st.sidebar.markdown(f"#### {label}（可多选）")
    
    toggle = st.sidebar.checkbox(
        "点击展开选项", 
        key=f"toggle_{label}",
        help='可选择多个选项，若不展开则视为"无所谓"'  # 使用单引号包裹双引号
    )
    
    if toggle:
        st.sidebar.caption("可选择多个选项")
        if custom_order:
            options = custom_order
        else:
            options = list(options_dict.keys())
            
        selected = []
        for option in options:
            if st.sidebar.checkbox(option, key=f"{label}_{option}"):
                selected.append(option)
                    
        return selected if selected else ["无所谓"]
    return ["无所谓"]

# 使用改进的多选框
marital_status = create_checkbox_select("婚姻状况", mappings["marital_status"])
property_status = create_checkbox_select("房产情况", mappings["property_status"])
hometown = create_checkbox_select("家庭所在地", mappings["hometown"], location_order)
current_location = create_checkbox_select("目前所在地", mappings["current_location"], location_order)
smoking_habit = create_checkbox_select("吸烟习惯", mappings["smoking_habit"])
drinking_habit = create_checkbox_select("饮酒习惯", mappings["drinking_habit"])
vision = create_checkbox_select("视力情况", mappings["vision"])

def filter_candidates(data, criteria):
    filtered = data[
        (data["age"] >= criteria["age"][0]) & (data["age"] <= criteria["age"][1]) &
        (data["height"] >= criteria["height"][0]) & (data["height"] <= criteria["height"][1]) &
        (data["face_score"] >= criteria["min_face_score"]) &
        (data["humor_score"] >= criteria["min_humor_score"]) &
        (data["sex_attract_score"] >= criteria["min_sex_attract_score"]) &
        (data["body_score"] >= criteria["min_body_score"]) &
        (data["education"] >= criteria["min_education"]) &
        (data["family_asset"] >= criteria["min_family_asset"]) &
        (data["personal_income"] >= criteria["min_personal_income"])
    ]
    
    # 处理单选的筛选条件
    if criteria["health_status"] != -1:
        filtered = filtered[filtered["health_status"] == criteria["health_status"]]
    if criteria["religion"] != -1:
        filtered = filtered[filtered["religion"] == criteria["religion"]]

    # 处理多选的筛选条件
    def filter_multiselect(df, field, selected_values):
        if "无所谓" in selected_values:
            return df
        return df[df[field].isin([mappings[field][val] for val in selected_values])]

    filtered = filter_multiselect(filtered, "marital_status", criteria["marital_status"])
    filtered = filter_multiselect(filtered, "property_status", criteria["property_status"])
    filtered = filter_multiselect(filtered, "hometown", criteria["hometown"])
    filtered = filter_multiselect(filtered, "current_location", criteria["current_location"])
    filtered = filter_multiselect(filtered, "smoking_habit", criteria["smoking_habit"])
    filtered = filter_multiselect(filtered, "drinking_habit", criteria["drinking_habit"])
    filtered = filter_multiselect(filtered, "vision", criteria["vision"])

    return filtered

criteria = {
    "age": age,
    "height": height,
    "min_education": education_order.index(education),
    "min_family_asset": family_asset_order.index(family_asset),
    "min_personal_income": personal_income_order.index(personal_income),
    "min_face_score": min_face_score,
    "min_humor_score": min_humor_score,
    "min_sex_attract_score": min_sex_attract_score,
    "min_body_score": min_body_score,
    "health_status": mappings["health_status"][health_status] if health_status != "无所谓" else -1,
    "religion": mappings["religion"][religion] if religion != "无所谓" else -1,
    "marital_status": marital_status,
    "property_status": property_status,
    "hometown": hometown,
    "current_location": current_location,
    "smoking_habit": smoking_habit,
    "drinking_habit": drinking_habit,
    "vision": vision
}

# 筛选数据
filtered_candidates = filter_candidates(data, criteria)

def format_result(data, filtered_candidates):
    total_candidates = len(data)  # 总人数作为基数
    
    # 计算符合条件的人数（应用调整因子）
    adjusted_candidates = min(len(filtered_candidates), total_candidates)
    
    perc = (adjusted_candidates / total_candidates)
    
    total_desired_chinese = int(700_000_000 * perc)
    
    st.markdown(
        """
        <style>
        .result-container {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        .main-number {
            color: #FF4B4B;
            font-size: 3em;
            font-weight: bold;
            padding: 0 0.2em;
            font-family: 'Arial', sans-serif;
        }
        .percentage {
            color: #FF4B4B;
            font-weight: bold;
            font-size: 1.5em;
            padding: 0 0.2em;
        }
        .description {
            font-size: 1.2em;
            line-height: 1.8;
            margin-bottom: 1rem;
        }
        .sub-description {
            color: #666;
            font-size: 1.1em;
            border-top: 1px solid #eee;
            padding-top: 1rem;
            margin-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        f"""
        <div class="result-container">
            <div class="description">
                平均每 「一百万」 中国男性中有 
                <span class="main-number">{adjusted_candidates:,}</span>
                人符合你的择偶要求，比例为
                <span class="percentage">{perc:.4%}</span>
            </div>
            <div class="sub-description">
                这意味着在全国约 7亿 男性中，大约有 {total_desired_chinese:,} 人符合你的要求。
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 在主程序中使用
format_result(data, filtered_candidates)