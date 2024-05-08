from django.shortcuts import render
from .models import Articles
from .serializers import ArticlesSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework import status, request
from django.http import HttpResponse
from rest_framework.views import APIView
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .sports_lexicon import sports_lexicon
from .sports_keywords import sports_keywords
import requests
from bs4 import BeautifulSoup
import spacy
import pytextrank


class CustomSentimentIntensityAnalyzer(SentimentIntensityAnalyzer):
    def __init__(self, custom_lexicon):
        super().__init__()
        self.lexicon.update(custom_lexicon)

# Initialize the custom analyzer with the sports lexicon
custom_analyzer = CustomSentimentIntensityAnalyzer(sports_lexicon)

# Function to analyze sentiment
def analyze_sentiment(text):
    sid_obj = SentimentIntensityAnalyzer()
    if any(keyword in text.lower() for keyword in sports_keywords):
        # If the sentence contains sports-related keywords, perform sentiment analysis
        #sentiment_dict = custom_analyzer.polarity_scores(text)
        sentiment_dict = sid_obj.polarity_scores(text)
        sentiment = ""
        if sentiment_dict['compound'] >= 0.05:
            sentiment = "Positive"
        elif sentiment_dict['compound'] <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        sentiment_dict["overall_sentiment"] = sentiment
        return sentiment_dict
    else:
        # If the sentence is not related to sports, return None
        return "Not sport related"

# Create your views here.

class ArticlesView(APIView):
    def post(self, request):
        # Get the URL from the request data
        url = request.data.get('url')
        
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find_all('h1')

            if title:
                title_text = title[0].text

            image_tag = soup.find('img')

            image_url = ""

            if image_tag:
                image_url = image_tag['src']
 
            # Find all paragraph elements
            paragraphs = soup.find_all('p')
            
            # Extract and concatenate text from all paragraph elements
            paragraph_content = ' '.join([paragraph.get_text() for paragraph in paragraphs])
            
            # Analyze sentiment of the extracted content
            sentiment_result = analyze_sentiment(paragraph_content)
            nlp = spacy.load("en_core_web_lg")
            nlp.add_pipe("textrank")
            doc = nlp(paragraph_content)

            for sent in doc._.textrank.summary(limit_sentences=5):
                print(sent)
            summary = '\n'.join(str(sent) for sent in doc._.textrank.summary(limit_sentences=5))
            
            # Prepare JSON response
            response_data = {
                #'paragraph_content': paragraph_content,
                'title': title_text,
                'image': image_url,
                'sentiment_result': sentiment_result,
                'summary': summary
            }
            
            # Return the JSON response
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # If the request was not successful, return an error response
            return Response({'error': 'Failed to retrieve content from the URL'}, status=status.HTTP_400_BAD_REQUEST)

