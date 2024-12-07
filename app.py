import streamlit as st
import pandas as pd
import json

# UI组件
@st.cache_data 
def load_data():
    data = pd.read_parquet("data/data_numeric.parquet")
    with open('data/mappings.json', "r", encoding="utf-8") as f:
        mappings = json.load(f)
    return data, mappings

def add_scoring_reference():
    """添加评分参考标准"""
    content = """
    <div style="background-color: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 1rem 0;">
        <h3 style="color: #333; font-size: 1.5rem;">评分参考标准</h3>
        <h4 style="color: #444; font-size: 1.2rem;">颜值评分参考</h4>
        <p style="color: #666;">3分：普通水平（参考：黄渤）</p>
        <p style="color: #666;">4分：较高水平（参考：胡歌）</p>
        <p style="color: #666;">5分：顶级水平（参考：吴彦祖、彭于晏）</p>
        <h4 style="color: #444; font-size: 1.2rem;">性吸引力评分参考</h4>
        <p style="color: #666;">3分：普通水平（参考：黄渤）</p>
        <p style="color: #666;">4分：较高水平（参考：胡歌）</p>
        <p style="color: #666;">5分：顶级水平（参考：吴彦祖、彭于晏）</p>
        <p style="color: #888; font-size: 0.9em;">注：1-2分暂不列举具体例子。以上参考均以公众人物巅峰期为准。</p>
    </div>
    """
    st.markdown(content, unsafe_allow_html=True)



def format_result(data, filtered_candidates, age_range):
    """格式化结果显示"""
    # 计算总体比例
    total_candidates = len(data)
    adjusted_candidates = len(filtered_candidates)
    total_perc = (adjusted_candidates / total_candidates)
    
    # 计算年龄段内的比例
    age_range_data = data[(data["age"] >= age_range[0]) & (data["age"] <= age_range[1])]
    age_range_filtered = filtered_candidates[
        (filtered_candidates["age"] >= age_range[0]) & 
        (filtered_candidates["age"] <= age_range[1])
    ]
    
    age_range_total = len(age_range_data)
    age_range_matched = len(age_range_filtered)
    age_range_perc = (age_range_matched / age_range_total) if age_range_total > 0 else 0
    
    # 显示结果
    st.markdown(
        f"""
        <div class="result-container" style="background-color:white; padding:2rem; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1); margin:1rem 0;">
            <div style="font-size:1.2em; line-height:1.8; margin-bottom:1rem;">
                平均每 「一百万」 中国男性中有 
                <span style="color:#FF4B4B; font-size:3em; font-weight:bold; padding:0 0.2em;">
                    {int(total_perc * 1_000_000):,}
                </span>
                人符合你的择偶要求，比例为
                <span style="color:#FF4B4B; font-weight:bold; font-size:1.5em; padding:0 0.2em;">
                    {total_perc:.4%}
                </span>
            </div>
            <div style="color:#666; font-size:1.1em; border-top:1px solid #eee; padding-top:1rem;">
                这意味着在全国约 7亿 男性中，大约有 {int(700_000_000 * total_perc):,} 人符合你的要求。
            </div>
        </div>
        
        <div class="result-container" style="background-color:white; padding:2rem; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1); margin:1rem 0;">
            <div style="font-size:1.2em; line-height:1.8; margin-bottom:1rem;">
                在你选择的 {age_range[0]}-{age_range[1]} 岁年龄段中，每 「一百万」 中国男性中有
                <span style="color:#FF4B4B; font-size:3em; font-weight:bold; padding:0 0.2em;">
                    {int(age_range_perc * 1_000_000):,}
                </span>
                人符合你的择偶要求，比例为
                <span style="color:#FF4B4B; font-weight:bold; font-size:1.5em; padding:0 0.2em;">
                    {age_range_perc:.4%}
                </span>
            </div>
            <div style="color:#666; font-size:1.1em; border-top:1px solid #eee; padding-top:1rem;">
                这个比例仅考虑了你选择的年龄段内的男性。
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_checkbox_select(label, mapping_key, mappings, custom_order=None):
    """创建多选框组件"""
    st.sidebar.markdown(f"#### {label}（可多选）")
    
    toggle = st.sidebar.checkbox(
        "点击展开选项", 
        key=f"toggle_{label}",
        help='可选择多个选项，若不展开则视为"无所谓"'
    )
    
    if toggle:
        st.sidebar.caption("可选择多个选项")
        if custom_order:
            options = custom_order
        else:
            options = list(mappings['mappings'][mapping_key].keys())
            
        selected = []
        for option in options:
            if st.sidebar.checkbox(option, key=f"{label}_{option}"):
                selected.append(option)
                    
        return selected if selected else ["无所谓"]
    return ["无所谓"]

def filter_candidates(data, criteria, mappings):
    """筛选符合条件的候选人"""
    filtered = data[
        (data["age"] >= criteria["age"][0]) & (data["age"] <= criteria["age"][1]) &
        (data["height"] >= criteria["height"][0]) & (data["height"] <= criteria["height"][1]) &
        (data["face_score"] >= criteria["min_face_score"]) &
        (data["humor_score"] >= criteria["min_humor_score"]) &
        (data["sex_attract_score"] >= criteria["min_sex_attract_score"]) &
        (data["body_score"] >= criteria["min_body_score"]) &
        (data["education"] >= criteria["min_education"]) &
        (data["personal_assets"] >= criteria["min_personal_assets"]) &
        (data["income"] >= criteria["min_personal_income"])
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
        return df[df[field].isin([mappings['mappings'][field][val] for val in selected_values])]

    filtered = filter_multiselect(filtered, "marital_status", criteria["marital_status"])
    filtered = filter_multiselect(filtered, "property_status", criteria["property_status"])
    filtered = filter_multiselect(filtered, "hometown", criteria["hometown"])
    filtered = filter_multiselect(filtered, "current_location", criteria["current_location"])
    filtered = filter_multiselect(filtered, "smoking_habit", criteria["smoking_habit"])
    filtered = filter_multiselect(filtered, "drinking_habit", criteria["drinking_habit"])
    filtered = filter_multiselect(filtered, "vision", criteria["vision"])

    return filtered

def main():
    """主程序"""
    # 加载数据
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
    
    # 显示评分参考
    add_scoring_reference()
    
    st.sidebar.header("筛选")

    # 用户输入筛选条件
    age = st.sidebar.slider("年龄范围", min_value=0, max_value=99, value=(18, 45))
    height = st.sidebar.slider("身高范围 (cm)", min_value=150, max_value=200, value=(150, 200))

    # 从 mappings 获取正确的选项顺序
    education_order = list(mappings['mappings']['education'].keys())
    personal_assets_order = list(mappings['mappings']['personal_assets'].keys())
    income_order = list(mappings['mappings']['income'].keys())
    location_order = list(mappings['mappings']['current_location'].keys())

    # 最低要求选项
    education = st.sidebar.selectbox("最低学历", options=education_order, index=0)
    personal_income = st.sidebar.selectbox("最低个人年收入", options=income_order, index=0)
    personal_assets = st.sidebar.selectbox("最低个人总资产", options=personal_assets_order, index=0)

    # 评分选项
    min_face_score = st.sidebar.slider("最低颜值评分", min_value=1, max_value=5, value=1)
    min_humor_score = st.sidebar.slider("最低幽默评分", min_value=1, max_value=5, value=1)
    min_sex_attract_score = st.sidebar.slider("最低性吸引力评分", min_value=1, max_value=5, value=1)
    min_body_score = st.sidebar.slider("最低身材评分", min_value=1, max_value=5, value=1)

    # 单选选项
    health_status = st.sidebar.radio(
        "健康状况", 
        options=["无所谓"] + list(mappings['mappings']["health_status"].keys()), 
        index=0
    )
    religion = st.sidebar.radio(
        "宗教信仰", 
        options=["无所谓"] + list(mappings['mappings']["religion"].keys()), 
        index=0
    )

    # 多选选项
    marital_status = create_checkbox_select("婚姻状况", "marital_status", mappings)
    property_status = create_checkbox_select("房产情况", "property_status", mappings)
    hometown = create_checkbox_select("家庭所在地", "hometown", mappings, location_order)
    current_location = create_checkbox_select("目前所在地", "current_location", mappings, location_order)
    smoking_habit = create_checkbox_select("吸烟习惯", "smoking_habit", mappings)
    drinking_habit = create_checkbox_select("饮酒习惯", "drinking_habit", mappings)
    vision = create_checkbox_select("视力情况", "vision", mappings)

    # 整理筛选条件
    criteria = {
        "age": age,
        "height": height,
        "min_education": mappings['mappings']['education'][education],
        "min_personal_assets": mappings['mappings']['personal_assets'][personal_assets],
        "min_personal_income": mappings['mappings']['income'][personal_income],
        "min_face_score": min_face_score - 1,
        "min_humor_score": min_humor_score - 1,
        "min_sex_attract_score": min_sex_attract_score - 1,
        "min_body_score": min_body_score - 1,
        "health_status": mappings['mappings']["health_status"][health_status] if health_status != "无所谓" else -1,
        "religion": mappings['mappings']["religion"][religion] if religion != "无所谓" else -1,
        "marital_status": marital_status,
        "property_status": property_status,
        "hometown": hometown,
        "current_location": current_location,
        "smoking_habit": smoking_habit,
        "drinking_habit": drinking_habit,
        "vision": vision
    }

    # 筛选数据并显示结果
    filtered_candidates = filter_candidates(data, criteria, mappings)
    format_result(data, filtered_candidates, age)

if __name__ == "__main__":
    main()