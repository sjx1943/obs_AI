from flask import Flask, render_template, request
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
# ... (其他导入)
llm = OpenAI(api_key='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')  # 替换为您的API密钥
prompt_template = PromptTemplate(input_variables=["question"], template="Question: {question}")
chain = prompt_template | llm
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    answer = None
    if request.method == 'POST':
        user_input = request.form['question']
        response = chain.invoke({"question": user_input})
        answer = response
    return render_template('index.html', answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
