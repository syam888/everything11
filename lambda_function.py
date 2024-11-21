import requests
from transformers import pipeline
import os
import markdown

# Step 1: Set your API Key from NewsAPI
API_KEY = 'd6f098e271eb4eb59c2b1f6812093639'

# Step 2: Define the endpoint and parameters
url = "https://newsapi.org/v2/top-headlines"
params = {
    'apiKey': API_KEY,
    'country': 'us',  # You can change to other countries like 'in' for India
    'category': 'technology',  # Choose categories like 'business', 'health', etc.
    'pageSize': 5  # Number of articles to fetch
}

# Function to convert Markdown to HTML
def convert_markdown_to_html(markdown_file, output_html_file):
    with open(markdown_file, 'r') as md_file:
        markdown_content = md_file.read()
    
    html_content = markdown.markdown(markdown_content)
    
    with open(output_html_file, 'w') as html_file:
        html_file.write(html_content)

# Step 3: Send the request to the NewsAPI endpoint
response = requests.get(url, params=params)

# Step 4: Check for successful response
if response.status_code == 200:
    news_data = response.json()
    articles = news_data.get('articles', [])
    
    # Step 5: Load the summarization pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # BART model is used

    # Initialize blog content
    blog_title = "This Week in Tech: Top Headlines"
    blog_introduction = "Here are the latest developments in technology. From groundbreaking innovations to critical industry shifts, stay informed!"
    blog_content = [f"# {blog_title}\n\n", f"## Introduction\n{blog_introduction}\n\n", "## Articles:\n"]

    seen_titles = set()  # To track duplicate articles
    
    # Step 6: Loop through articles and summarize descriptions
    for article in articles:
        title = article.get('title')
        description = article.get('description')
        article_url = article.get('url')

        # Skip if the title has been processed already (avoid duplicates)
        if title in seen_titles:
            continue
        seen_titles.add(title)

        # Add article title and URL to blog content
        blog_content.append(f"### {title}\n")
        blog_content.append(f"**[Read more]({article_url})**\n")

        # Check if description is available and long enough for summarization
        if description and len(description.split()) > 20:
            input_length = len(description.split())
            max_len = min(60, input_length)  # Adjust max_length based on input length
            min_len = max(20, int(input_length * 0.5))  # Ensure min_length is meaningful

            # Perform summarization
            summary = summarizer(description, max_length=max_len, min_length=min_len, do_sample=False)
            blog_content.append(f"**Summary**: {summary[0]['summary_text']}\n\n")
        else:
            # Handle missing or incomplete descriptions
            blog_content.append(f"**Summary**: Description is too brief to summarize effectively.\n\n")

    # Add conclusion
    blog_conclusion = "Stay tuned for more updates in the tech world!"
    blog_content.append(f"## Conclusion\n{blog_conclusion}\n")

    # Save the blog content to a markdown file (use /tmp/ directory for AWS Lambda)
    markdown_file_path = "/tmp/weekly_tech_blog.md"
    with open(markdown_file_path, "w") as f:
        f.write("\n".join(blog_content))

    print(f"Blog content saved to {markdown_file_path}")

    # Convert Markdown to HTML
    html_file_path = "/tmp/weekly_tech_blog.html"
    convert_markdown_to_html(markdown_file_path, html_file_path)
    print(f"HTML content saved to {html_file_path}")

else:
    print(f"Failed to fetch news: {response.status_code}")