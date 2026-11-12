
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from collections import Counter

# 1. 페이지 설정
st.set_page_config(
    page_title="아이리스 붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

# 2. 데이터 준비
@st.cache_data
def get_iris_data():
    iris = load_iris()

    X = pd.DataFrame(
        iris.data[:, [2, 3]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    y = pd.Series(iris.target, name="품종 번호")

    names = [
        "Setosa (세토사)",
        "Versicolor (버시컬러)",
        "Virginica (버지니카)"
    ]

    return X, y, names


X, y, species_names = get_iris_data()

# 3. KNN 모델 학습
@st.cache_resource
def make_model():
    classifier = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=5))
    ])

    classifier.fit(X, y)
    return classifier


model = make_model()

# 4. 화면 구성
st.title("🌸 아이리스 붓꽃 품종 예측")
st.write(
    "꽃잎 길이와 너비를 입력하면 KNN 알고리즘으로 "
    "붓꽃 품종을 예측해 줍니다."
)

st.subheader("1. 꽃잎 크기 입력하기")

input_col1, input_col2 = st.columns(2)

with input_col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=1.0,
        max_value=7.0,
        value=4.5,
        step=0.1,
        format="%.1f"
    )

with input_col2:
    petal_width = st.number_input(
        "🌼 꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.5,
        step=0.1,
        format="%.1f"
    )

user_input = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=["꽃잎 길이", "꽃잎 너비"]
)

# 5. 품종 예측
predicted_class = int(model.predict(user_input)[0])
predicted_name = species_names[predicted_class]

probabilities = model.predict_proba(user_input)[0]

# 가장 가까운 데이터 5개
distances, neighbor_indices = model.kneighbors(
    user_input,
    n_neighbors=5
)

neighbor_indices = neighbor_indices[0]
distances = distances[0]

neighbor_classes = y.iloc[neighbor_indices].astype(int).tolist()
votes = Counter(neighbor_classes)
winning_votes = votes.get(predicted_class, 0)

# 6. 예측 결과
st.divider()
st.subheader("2. 예측 결과")

result_col, probability_col = st.columns([1, 2])

with result_col:
    st.metric("예측된 품종", predicted_name)

    st.success(
        f"가장 가까운 데이터 5개 중 "
        f"{winning_votes}개가 {predicted_name}입니다."
    )

with probability_col:
    st.write("품종별 예측 확률")

    probability_table = pd.DataFrame({
        "품종": species_names,
        "예측 확률(%)": np.round(
            probabilities * 100, 1
        )
    }).set_index("품종")

    st.bar_chart(probability_table)

# 7. 분류 영역 그래프
st.divider()
st.subheader("3. 품종 분류 시각화")

x_min = 0.5
x_max = 7.5
y_min = 0.0
y_max = 2.8

grid_x, grid_y = np.meshgrid(
    np.linspace(x_min, x_max, 220),
    np.linspace(y_min, y_max, 220)
)

grid_df = pd.DataFrame({
    "꽃잎 길이": grid_x.ravel(),
    "꽃잎 너비": grid_y.ravel()
})

grid_classes = model.predict(grid_df).reshape(grid_x.shape)

fig, ax = plt.subplots(figsize=(10, 7))

# 품종별 예측 영역
ax.contourf(
    grid_x,
    grid_y,
    grid_classes,
    levels=[-0.5, 0.5, 1.5, 2.5],
    colors=["#8ecae6", "#ffd166", "#cdb4db"],
    alpha=0.35
)

# 기존 데이터 표시
point_colors = [
    "#247BA0",
    "#E09F3E",
    "#805AD5"
]

for class_id, species in enumerate(species_names):

    selected = (y == class_id)

    ax.scatter(
        X.loc[selected, "꽃잎 길이"],
        X.loc[selected, "꽃잎 너비"],
        color=point_colors[class_id],
        label=species,
        s=38,
        alpha=0.8,
        edgecolors="white",
        linewidths=0.4
    )

# 가까운 이웃 5개 강조
nearby = X.iloc[neighbor_indices]

ax.scatter(
    nearby["꽃잎 길이"],
    nearby["꽃잎 너비"],
    s=170,
    facecolors="none",
    edgecolors="black",
    linewidths=1.7,
    label="가장 가까운 이웃 5개",
    zorder=5
)

# 사용자 입력값: 초록색 별
ax.scatter(
    petal_length,
    petal_width,
    color="green",
    marker="*",
    s=420,
    edgecolors="black",
    linewidths=0.8,
    label="내가 입력한 값",
    zorder=10
)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.set_xlabel("꽃잎 길이 (cm)")
ax.set_ylabel("꽃잎 너비 (cm)")
ax.set_title("KNN 붓꽃 품종 분류 영역")

ax.legend()
ax.grid(alpha=0.2)

st.pyplot(fig)
plt.close(fig)

st.caption(
    "초록색 별은 입력값, 배경색은 모델이 예측하는 품종 영역, "
    "검은색 테두리는 가장 가까운 학습 데이터 5개입니다."
)

# 8. 예측 이유 분석
st.divider()
st.subheader("4. 왜 이 품종으로 예측했을까요?")

vote_rows = []

for class_id, species in enumerate(species_names):

    count = votes.get(class_id, 0)

    vote_rows.append({
        "품종": species,
        "가까운 이웃 개수": count,
        "투표 비율(%)": count * 20
    })

vote_df = pd.DataFrame(vote_rows)

vote_df = vote_df.sort_values(
    by="가까운 이웃 개수",
    ascending=False
)

st.write("### 🗳️ 가까운 이웃 5개의 투표 결과")

st.dataframe(
    vote_df,
    use_container_width=True
)

# 가까운 데이터 상세 정보
neighbor_table = X.iloc[neighbor_indices].copy()

neighbor_table.insert(
    0,
    "이웃 순서",
    [1, 2, 3, 4, 5]
)

neighbor_table["품종"] = [
    species_names[int(y.iloc[index])]
    for index in neighbor_indices
]

neighbor_table["표준화 거리"] = distances

st.write("### 🔎 가까운 데이터 5개 상세 정보")

st.dataframe(
    neighbor_table.round(3),
    use_container_width=True,
    hide_index=True
)

st.info(
    f"KNN은 입력값과 가까운 데이터 5개를 비교합니다. "
    f"그중 {winning_votes}개가 {predicted_name}이므로 "
    f"다수결에 따라 {predicted_name}으로 예측했습니다."
)

# 9. 알고리즘 설명
with st.expander("📚 KNN 알고리즘 알아보기"):

    st.markdown("""
    **KNN(최근접 이웃)이란?**

    1. 기존 붓꽃 데이터의 꽃잎 길이와 너비를 준비합니다.
    2. 사용자가 입력한 값과 기존 데이터 사이의 거리를 계산합니다.
    3. 가장 가까운 데이터 5개를 찾습니다.
    4. 5개 중 가장 많이 나타난 품종을 예측합니다.

    **표준화를 하는 이유**

    꽃잎 길이와 너비의 측정 범위가 다르므로
    두 변수의 크기 차이가 거리 계산에 미치는 영향을
    줄이기 위해 표준화합니다.

    **그래프 읽는 방법**

    - 파란색·주황색·보라색 점: 기존 붓꽃 데이터
    - 초록색 별: 사용자 입력값
    - 배경색: 모델이 예측하는 품종 영역
    - 검은색 테두리: 가장 가까운 데이터 5개
    """)

st.caption(
    "학습 데이터: Scikit-learn Iris 데이터셋 | "
    "분류 알고리즘: KNN (K=5)"
)

