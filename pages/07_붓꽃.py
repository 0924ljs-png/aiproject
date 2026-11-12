
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from collections import Counter

# 페이지 설정
st.set_page_config(
    page_title="아이리스 붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 붓꽃 품종 예측")
st.write("꽃잎 길이와 너비를 입력하면 붓꽃 품종을 예측해 줍니다.")

# 1. 데이터 불러오기
@st.cache_data
def load_data():
    iris = load_iris()

    X = pd.DataFrame(
        iris.data[:, [2, 3]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    y = pd.Series(iris.target)

    species_names = [
        "Setosa (세토사)",
        "Versicolor (버시컬러)",
        "Virginica (버지니카)"
    ]

    return X, y, species_names


X, y, species_names = load_data()

# 2. KNN 모델 생성
@st.cache_resource
def train_model():
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=5))
    ])

    model.fit(X, y)
    return model


model = train_model()

# 3. 사용자 입력
st.subheader("🌷 꽃잎 크기를 입력하세요.")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.slider(
        "꽃잎 길이 (cm)",
        1.0, 7.0, 4.5, 0.1
    )

with col2:
    petal_width = st.slider(
        "꽃잎 너비 (cm)",
        0.1, 2.5, 1.5, 0.1
    )

user_input = np.array([[petal_length, petal_width]])

# 4. 품종 예측
predicted_number = int(model.predict(user_input)[0])
predicted_species = species_names[predicted_number]

probabilities = model.predict_proba(user_input)[0]

# 가장 가까운 이웃 5개
distances, neighbor_indices = model.kneighbors(
    user_input,
    n_neighbors=5
)

neighbor_indices = neighbor_indices[0]
distances = distances[0]

neighbor_species_numbers = y.iloc[neighbor_indices].tolist()
vote_counts = Counter(neighbor_species_numbers)

# 5. 예측 결과
st.divider()
st.subheader("🔍 예측 결과")

result_col1, result_col2 = st.columns([1, 2])

with result_col1:
    st.metric("예측 품종", predicted_species)
    st.success("품종 예측이 완료되었습니다!")

with result_col2:
    st.write("품종별 예측 확률")

    probability_df = pd.DataFrame({
        "품종": species_names,
        "예측 확률(%)": probabilities * 100
    }).sort_values("예측 확률(%)", ascending=False)

    st.bar_chart(
        probability_df.set_index("품종"),
        y="예측 확률(%)"
    )

# 6. 그래프의 예측 영역 계산
st.divider()
st.subheader("📊 붓꽃 품종 분류 시각화")

x_min = max(0.5, X["꽃잎 길이"].min() - 0.5)
x_max = X["꽃잎 길이"].max() + 0.5
y_min = max(0.0, X["꽃잎 너비"].min() - 0.3)
y_max = X["꽃잎 너비"].max() + 0.3

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 250),
    np.linspace(y_min, y_max, 250)
)

grid_points = np.c_[xx.ravel(), yy.ravel()]

grid_predictions = model.predict(grid_points)
Z = grid_predictions.reshape(xx.shape)

# 7. 그래프 그리기
fig, ax = plt.subplots(figsize=(10, 7))

# 품종별 예측 영역
ax.contourf(
    xx,
    yy,
    Z,
    alpha=0.18,
    cmap=plt.cm.Set2,
    levels=[-0.5, 0.5, 1.5, 2.5]
)

colors = ["#2878B5", "#F39C34", "#9467BD"]

# 기존 붓꽃 데이터 표시
for class_number, species in enumerate(species_names):

    mask = (y == class_number)

    ax.scatter(
        X.loc[mask, "꽃잎 길이"],
        X.loc[mask, "꽃잎 너비"],
        color=colors[class_number],
        label=species,
        alpha=0.75,
        s=42,
        edgecolors="white"
    )

# 가장 가까운 이웃 5개 강조
neighbor_data = X.iloc[neighbor_indices]

ax.scatter(
    neighbor_data["꽃잎 길이"],
    neighbor_data["꽃잎 너비"],
    s=180,
    facecolors="none",
    edgecolors="black",
    linewidths=1.8,
    label="Nearest 5 neighbors"
)

# 사용자가 입력한 값: 초록색 별
ax.scatter(
    petal_length,
    petal_width,
    color="green",
    marker="*",
    s=450,
    edgecolors="black",
    label="Your input",
    zorder=10
)

ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)
ax.set_title("Iris KNN Classification Map", fontsize=15)

ax.legend()
ax.grid(alpha=0.2)

st.pyplot(fig)
plt.close(fig)

st.caption(
    "초록색 별은 사용자 입력값입니다. "
    "배경색은 각 위치에서 예측되는 품종 영역입니다. "
    "검은색 테두리는 가장 가까운 데이터 5개입니다."
)

# 8. 예측 이유 설명
st.divider()
st.subheader("💡 왜 이 품종으로 예측되었을까요?")

st.write(
    "KNN은 입력값과 기존 데이터 사이의 거리를 계산하고 "
    "가장 가까운 데이터 5개의 품종을 비교합니다."
)

vote_rows = []

for class_number in range(len(species_names)):

    count = vote_counts.get(class_number, 0)

    vote_rows.append({
        "품종": species_names[class_number],
        "가까운 이웃 개수": count,
        "투표 비율(%)": count / 5 * 100
    })

vote_df = pd.DataFrame(vote_rows).sort_values(
    "가까운 이웃 개수",
    ascending=False
)

st.write("### 🗳️ 품종별 투표 결과")

st.dataframe(
    vote_df,
    use_container_width=True,
    hide_index=True
)

# 가장 가까운 데이터 상세 정보
st.write("### 🔎 가장 가까운 데이터 5개")

neighbor_detail = X.iloc[neighbor_indices].copy()

neighbor_detail["품종"] = [
    species_names[int(y.iloc[index])]
    for index in neighbor_indices
]

neighbor_detail["표준화 거리"] = distances

neighbor_detail.index = range(1, 6)
neighbor_detail.index.name = "가까운 순서"

st.dataframe(
    neighbor_detail.round(3),
    use_container_width=True
)

winner_votes = vote_counts.get(predicted_number, 0)

st.info(
    f"가장 가까운 데이터 5개 중 {winner_votes}개가 "
    f"{predicted_species} 품종입니다. "
    "따라서 다수결 원리에 따라 이 품종으로 분류했습니다."
)

# 9. 머신러닝 원리 설명
with st.expander("📚 KNN 알고리즘 알아보기"):

    st.markdown("""
    **KNN이란?**

    1. 기존 붓꽃 데이터의 꽃잎 길이와 너비를 학습합니다.
    2. 새로운 입력값과 기존 데이터 사이의 거리를 계산합니다.
    3. 가장 가까운 데이터 5개를 찾습니다.
    4. 가장 많이 등장한 품종을 예측합니다.

    **표준화를 하는 이유**

    두 변수의 측정 범위 차이가 거리 계산에
    지나치게 영향을 주지 않도록 표준화합니다.

    **그래프 읽는 방법**

    - 파란색, 주황색, 보라색 점: 기존 데이터
    - 초록색 별: 사용자 입력값
    - 배경색: 품종별 예측 영역
    - 검은색 테두리: 가까운 데이터 5개
    """)

st.caption(
    "학습 데이터: Scikit-learn Iris 데이터셋 | "
    "알고리즘: KNN (K=5)"
)
