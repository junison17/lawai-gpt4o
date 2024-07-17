import streamlit as st
import openai
import os
from dotenv import load_dotenv
import requests
import json
import base64
from serpapi import GoogleSearch

# 환경변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# SerpAPI 키 설정
serpapi_key = os.getenv("SERPAPI_KEY")

# 팀 멤버 정의
team_members = ["판사", "검사", "변호사 1", "변호사 2 (시니어)", "법학 교수"]

# 스트림릿 앱 제목 설정
st.title("법률 자문 AI 팀")

# SerpAPI를 사용하여 인터넷에서 정보 검색하는 함수
def search_internet(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])[:3]

# 사용자 입력 받기
user_input = st.text_area("법률 문의 사항을 입력해주세요:")

# 인터넷 검색 버튼
if st.button("인터넷 검색"):
    if user_input:
        with st.spinner("인터넷에서 관련 정보를 검색 중입니다..."):
            search_results = search_internet(user_input)
            st.subheader("검색 결과")
            for result in search_results:
                st.write(f"제목: {result['title']}")
                st.write(f"내용: {result['snippet']}")
                st.write(f"URL: {result['link']}")
                st.write("---")
    else:
        st.warning("검색할 내용을 입력해주세요.")

# 자문 요청 버튼
if st.button("자문 요청"):
    if user_input:
        # 인터넷 검색 결과 가져오기
        search_results = search_internet(user_input)
        
        # 검색 결과를 문자열로 변환
        search_info = "\n".join([f"제목: {result['title']}\n내용: {result['snippet']}\nURL: {result['link']}\n" for result in search_results])
        
        messages = [
            {"role": "system", "content": "당신은 법률 자문 AI 팀의 일원입니다. 팀은 판사, 검사, 변호사 1, 변호사 2 (시니어), 법학 교수로 구성되어 있습니다. 팀원은 수직적 관계가 아닌 수평적 관계로 최선의 목적을 달성하기위해 서로 의견을 주고받고 , 판사는 사용자에게 최종보고서를 이해하기 쉽도록 다양한 방면으로 편집하여 사용자에게 제출한다."
             "글의 내용은 사실에 입각해서 작성해야하며, 성의없는 몇줄의 글은 제출하지 않는다. 팀원들이 심사숙고 하고 서로 커뮤니케이션을 하며, 회의적인 비판과 결과가 좋지 않을것 같은 내용은 다시 작성해달라고 요청할수 있다. 한마디로 AI 팀원들이 판사의 주도하에 토론을 하는것이다. 토론을 마친후 판사는 회의록을 작성해서 사용자에게 팀원들의 의견을 요약해서 제출하고 최종적으로 판사가 모든 내용을 판단하여 사용자에게 제출한다. 글의 길이는 성의없이 짦게 쓰지 않고 사용자가 납득이 가도록 예시나 기타 관련있는 사실내용 판례를 제출해서 사용자의 이해를 돕는다. 팀원들의 역할을 명확히 한다. 조사는 변호사들이하고, 현재 시점에서 법이 개정되었는지 법리의 오류가 없는지 검사가 확인한다. 판사는 변호가와 검사의 내용을 모두 분석한다. 팀원의 목표는 피해자가 억울하게 당하는것을 막는것이다.   다음은 관련된 인터넷 검색 결과입니다:\n\n" + search_info},
            {"role": "user", "content": user_input}
        ]

        # API 요청
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            stream=True
        )

        # 결과를 담을 컨테이너 생성
        result_container = st.empty()
        full_response = ""

        # 스트리밍 응답 처리
        for chunk in response:
            if chunk.choices[0].delta.get("content"):
                full_response += chunk.choices[0].delta.content
                result_container.markdown(full_response)

        # 전체 응답을 팀원별로 분리
        team_responses = full_response.split("\n\n")

        # 팀원별 응답 표시
        for member, response in zip(team_members, team_responses):
            st.subheader(member)
            st.write(response)

        # 다운로드 버튼 생성
        def get_binary_file_downloader_html(bin_file, file_label='File'):
            bin_str = base64.b64encode(bin_file).decode()
            href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">다운로드 {file_label}</a>'
            return href

        download_button = st.button("결과 다운로드")
        if download_button:
            # 결과를 텍스트 파일로 저장
            with open("legal_advice.txt", "w", encoding="utf-8") as f:
                f.write(full_response)
            
            # 다운로드 링크 생성
            with open("legal_advice.txt", "rb") as f:
                st.markdown(get_binary_file_downloader_html(f.read(), 'legal_advice.txt'), unsafe_allow_html=True)

    else:
        st.warning("문의 사항을 입력해주세요.")

# 추가 정보 링크
st.sidebar.title("추가 정보")
if st.sidebar.button("관련 법령 검색"):
    # 법령 정보 검색 (예시: 국가법령정보센터)
    url = "https://www.law.go.kr/LSW/lsInfoP.do?efYd=20230101&lsiSeq=246753#0000"
    st.sidebar.markdown(f"[국가법령정보센터]({url})")

if st.sidebar.button("판례 검색"):
    # 판례 검색 (예시: 대법원 종합법률정보)
    url = "https://glaw.scourt.go.kr/wsjo/intesrch/sjo022.do"
    st.sidebar.markdown(f"[대법원 종합법률정보]({url})")

# 한글 주석
"""
이 앱은 법률 자문 AI 팀을 시뮬레이션합니다.
주요 기능:
1. 사용자의 법률 문의 입력 받기
2. SerpAPI를 사용한 인터넷 검색
3. OpenAI API를 사용한 AI 팀의 자문 생성
4. 자문 결과 다운로드
5. 관련 법령 및 판례 검색 링크 제공
"""