from flask import Flask, request, render_template
import openai
import time

app = Flask(__name__)

openai.api_key = 'sk-proj-22oxxhgdAt4UgVaht4QyT3BlbkFJRIJ6cMn8pvSZCmyLA19X'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_text():
    input_text = request.form.get('text')
    if not input_text:
        return "No text provided"
    
    corrected_text, messages = correct_text(input_text)
    return render_template('result.html', corrected_text=corrected_text, messages=messages)

def correct_text(input_text):
    # Retry logic
    max_retries = 5
    retries = 0
    messages = []
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that corrects text."
                    },
                    {
                        "role": "user",
                        "content": f"Correct the following text: {input_text}"
                    }
                ]
            )
            return response['choices'][0]['message']['content'].strip(), messages
        except openai.error.RateLimitError:
            retries += 1
            wait_time = 2 ** retries  # Exponential backoff
            message = f"Rate limit exceeded. Retrying in {wait_time} seconds..."
            messages.append(message)
            print(message)
            time.sleep(wait_time)
        except openai.error.OpenAIError as e:
            return f"An error occurred: {str(e)}", messages
    return "Failed to get a response after several retries. Please try again later.", messages

if __name__ == '__main__':
    app.run(debug=True)