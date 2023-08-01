import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import html

def download_pdf(url):
    try:
        api_url = "https://api.askyourpdf.com/v1/api/download_pdf"
        headers = {"x-api-key": "ask_84362ce8044a2b097e08584435abae46"}
        params = {"url": url}
        response = requests.post(api_url, headers=headers, params=params)
        print("PDF download response:", response.json())
        return response.json().get("docId", None)
    except Exception as e:
        print("Error in download_pdf:", str(e))
        return None

def query_pdf(doc_id, query):
    try:
        api_url = f"https://api.askyourpdf.com/v1/chat/{doc_id}"
        headers = {"x-api-key": "ask_84362ce8044a2b097e08584435abae46", "Content-Type": "application/json"}
        data = [
            {
                "sender": "User",
                 "message": query
            }
        ] 
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        
        print("PDF query response:", response.json())

        if response.status_code == 200:
            result_text = response.json().get('answer', {}).get('message', '')
            if result_text:
                print("PDF query successful, received result:", result_text)
            else:
                print("PDF query unsuccessful, no result received")
            return response.json()
        else:
            print('Error:', response.status_code)


    except Exception as e:
        print("Error in query_pdf:", str(e))
        return None

def get_title_and_authors(master_url):
    try:
        response = requests.get(master_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', class_='title mathjax').text.strip()
        print(title)
        title = title.replace('Title: ', '')  # Remove 'Title: ' from the beginning
        print(title)
        authors = soup.find('div', class_='authors').text.strip()
        print(authors)
        return title, authors
    except Exception as e:
        print("Error in get_title_and_authors:", str(e))
        return None, None


# The rest of the code goes here...

st.title('Arithearcher')
st.caption('このアプリはURLで指定した論文の内容をお好みの観点でまとめることができます。')

url = st.text_input('Target Paper URL')

research_type = st.radio(
    'Research Point',
    ('Arithearcherにおまかせ', '自分で指定')
)

user_prompt = ''
checkbox_options = ['タイトル', '著者', '概要', '主張', '他の技術との優位性', '実験方法', '実験結果', '将来の展望']
checkbox_queries = {
    'タイトル': '本論文に対するタイトルを記載してください。',
    '著者': '本論文に対する著者を見つけて、著者の氏名と可能であれば所属機関を列挙してください。',
    '概要': '本論文の要点を押さえて簡潔にまとめてください。',
    '主張': '本論文における一番の主張はどのようなものか詳細に、かつ分かりやすく、簡潔にまとめてください。',
    '他の技術との優位性': '他の技術との優位性セクションを見つけて、この論文で提案されている技術が他の技術と比べてどのような優位性を持つのか明確に説明してください。',
    '実験方法': '実験方法セクションを見つけて、この論文で行われた実験の手法を具体的に説明してください。',
    '実験結果': '実験結果セクションを見つけて、この論文で得られた主要な実験結果を要点を押さえてまとめてください。',
    '将来の展望': '将来の展望セクションを見つめて、この論文の結論部分で述ふされている将来の展望を簡潔にまとめてください。',
}

checked_options = []

if research_type == 'Arithearcherにおまかせ':
    cols = st.columns(2)
    for i, option in enumerate(checkbox_options):
        checked = cols[i%2].checkbox(option)
        if checked:
            checked_options.append(option)
elif research_type == '自分で指定':
    user_prompt = st.text_input('ここにどのような観点で論文を調査したいか記述してください')

output_areas = {option: st.empty() for option in checkbox_options}

if st.button('RESEARCH'):
    if url:
        doc_id = download_pdf(url)
        if doc_id:
            if research_type == 'Arithearcherにおまかせ':
                results_dict = {}  
                paper_id = url.split('/')[-1].replace('.pdf', '')
                master_url = f"https://arxiv.org/abs/{paper_id}"
                title, authors = get_title_and_authors(master_url)
                print(f"Title obtained: {title}")
                for option in checked_options:
                    if option == 'タイトル':
                        results_dict[option] = title
                    elif option == '著者':
                        results_dict[option] = authors
                    else:
                        query = f"この「{title}」の論文に対して" + checkbox_queries[option]
                        print(f"Generated query: {query}")
                        results = query_pdf(doc_id, query)
                        if results:
                            result_text = results.get('answer', {}).get('message', '')
                            results_dict[option] = result_text if result_text else '情報なし'
                for option, result_text in results_dict.items():
                    escaped_text = html.escape(result_text)
                    if option in ['タイトル', '著者']:  # Add this line
                        output_areas[option].text(f"{option}: {escaped_text}")  # Use text for title and author
                    else:
                       output_areas[option].markdown(f"**{option}**: {escaped_text}")  # Use markdown for others
            elif research_type == '自分で指定':
                results = query_pdf(doc_id, user_prompt)
                if results:
                    result_text = results.get('answer', {}).get('message', '')
                    output_area.text_area(result_text)
                else:
                    st.error("Error occurred during querying the PDF.")
        else:
            st.error("Error occurred during PDF download.")
    else:
        st.error("Please enter a URL.")
