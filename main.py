import streamlit as st
st.title('이민서는 바보다')
a=st.text_input('이름이나 말해')
b=st.selectbox('좋아하는 음식이나 말해ㅋㅋ',['떡볶이','마라탕','고구마피자','떡',])
if st.button('인사말 생성'):
  st.write('반갑다')
  st.info(a+'님 안녕항셍용')
  st.warning(b+'를 좋아하나보넹')
  st.error('잘 부타켕')
  st.balloons()
