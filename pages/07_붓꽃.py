
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from collections import Counter

# 1. 페이지 설정
st.set_page_config(
    page_title="아이리스 붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 붓꽃 품종 예측")
st.write(
    "꽃잎 길이와 꽃잎 너비를 입력하면 "
    "KNN 알고리즘으로 붓꽃 품종을 예측합니다."
)

# 2. 데이터 준비
@st.cache_data
def load_training_data():
    iris = load_iris()

    X = iris.data[:, [2, 3]].astype(float)
    y = iris.target.astype(int)

    names = [
        "Setosa (세토사)",
        "Versicolor (버시컬러)",
        "Virginica (버지니카)"
    ]

    return X, y, names


X, y, species_names = load_training_data()

# 3. 모델 학습
@st.cache_resource
def train_classifier():
    model = make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=5)
    )

    model.fit(X, y)
    return model


model = train_classifier()

# 4. 사용자 입력
st.subheader("1. 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌷 꽃잎 길이 (cm)",
        min_value=1.0,
        max_value=7.0,
        value=4.5,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "🌼 꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.5,
        step=0.1,
        format="%.1f"
    )

user_point = np.array(
    [[petal_length, petal_width]],
    dtype=float
)

# 5. 품종 예측
predicted_class = int(model.predict(user_point)[0])
predicted_species = species_names[predicted_class]

# 최근접 5개 데이터의 품종별 투표 비율
class_votes = model.predict_proba(user_point)[0]

# 표준화된 입력값으로 최근접 이웃 검색
scaled_point = model.named_steps[
    "standardscaler"
].transform(user_point)

distances, neighbor_indices = model.named_steps[
    "kneighborsclassifier"
].kneighbors(scaled_point, n_neighbors=5)

neighbor_indices = neighbor_indices[0]
distances = distances[0]

neighbor_labels = y[neighbor_indices]
vote_counts = Counter(neighbor_labels.tolist())

winning_votes = vote_counts.get(predicted_class, 0)

# 6. 예측 결과
st.divider()
st.subheader("2. 예측 결과")

left, right = st.columns([1, 2])

with left:
    st.metric(
        "예측된 붓꽃 품종",
        predicted_species
    )

    st.success(
        f"가장 가까운 데이터 5개 중 "
        f"{winning_votes}개가 이 품종입니다."
    )

with right:
    st.write("**품종별 투표 비율**")

    vote_df = pd.DataFrame({
        "품종": species_names,
        "투표 비율(%)": np.round(
            class_votes * 100, 1
        )
    }).set_index("품종")

    st.bar_chart(vote_df)

# 7. 분류 영역 그래프
st.divider()
st.subheader("3. 품종 분류 시각화")

st.write(
    "초록색 별은 사용자가 입력한 값이며, "
    "배경색은 모델이 예측하는 품종 영역입니다."
)

x_min, x_max = 0.8, 7.2
y_min, y_max = 0.0, 2.8

grid_x, grid_y = np.meshgrid(
    np.linspace(x_min, x_max, 180),
    np.linspace(y_min, y_max, 180)
)

grid_points = np.column_stack((
    grid_x.ravel(),
    grid_y.ravel()
))

grid_predictions = model.predict(
    grid_points
).reshape(grid_x.shape)

fig, ax = plt.subplots(figsize=(10, 7))

# 예측 영역
ax.contourf(
    grid_x,
    grid_y,
    grid_predictions,
    levels=[-0.5, 0.5, 1.5, 2.5],
    colors=[
        "#9BD3E8",
        "#FFE09A",
        "#D7B8E5"
    ],
    alpha=0.45
)

# 기존 붓꽃 데이터
point_colors = [
    "#247BA0",
    "#D98C24",
    "#8055A5"
]

for class_id, species in enumerate(species_names):

    mask = (y == class_id)

    ax.scatter(
        X[mask, 0],
        X[mask, 1],
        color=point_colors[class_id],
        label=species,
        s=35,
        alpha=0.8,
        edgecolors="white",
        linewidths=0.4
    )

# 가까운 데이터 5개
neighbors = X[neighbor_indices]

ax.scatter(
    neighbors[:, 0],
    neighbors[:, 1],
    s=160,
    facecolors="none",
    edgecolors="black",
    linewidths=1.5,
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
    label="사용자 입력값",
    zorder=10
)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

ax.set_xlabel("꽃잎 길이 (cm)")
ax.set_ylabel("꽃잎 너비 (cm)")
ax.set_title("KNN 붓꽃 품종 분류 지도")

ax.legend(loc="best")
ax.grid(alpha=0.2)

st.pyplot(fig)
plt.close(fig)

# 8. 예측 이유
st.divider()
st.subheader("4. 왜 이 품종으로 예측했을까요?")

st.write(
    f"가장 가까운 데이터 5개 중 "
    f"**{winning_votes}개**가 "
    f"**{predicted_species}**입니다."
)

vote_detail = pd.DataFrame({
    "품종": species_names,
    "가까운 이웃 개수": [
        vote_counts.get(i, 0)
        for i in range(3)
    ],
    "투표 비율(%)": [
        vote_counts.get(i, 0) * 20
        for i in range(3)
    ]
})

st.dataframe(
    vote_detail,
    use_container_width=True,
    hide_index=True
)

# 가까운 데이터 상세 정보
neighbor_df = pd.DataFrame({
    "가까운 순서": [1, 2, 3, 4, 5],
    "꽃잎 길이(cm)": neighbors[:, 0],
    "꽃잎 너비(cm)": neighbors[:, 1],
    "품종": [
        species_names[int(label)]
        for label in neighbor_labels
    ],
    "표준화 거리": distances
})

st.write("**가장 가까운 데이터 5개**")

st.dataframe(
    neighbor_df.round(3),
    use_container_width=True,
    hide_index=True
)

# 9. 알고리즘 설명
with st.expander("📚 KNN 알고리즘 알아보기"):

    st.markdown("""
    **KNN이란?**

    1. 기존 붓꽃 데이터의 꽃잎 길이와 너비를 준비합니다.
    2. 입력값과 기존 데이터 사이의 거리를 계산합니다.
    3. 가장 가까운 데이터 5개를 찾습니다.
    4. 가장 많이 등장한 품종을 예측합니다.

    **그래프 읽는 방법**

    - 파란색·주황색·보라색 점: 기존 붓꽃 데이터
    - 초록색 별: 사용자 입력값
    - 배경색: 품종별 예측 영역
    - 검은색 테두리: 가장 가까운 데이터 5개
    """)

st.caption(
    "학습 데이터: Scikit-learn Iris 데이터 | "
    "알고리즘: KNN (K=5)"
)

