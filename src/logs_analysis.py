#src/logs_analysis.py
from src.custom_exception import CustomException
from prompt_templates.templates import logs_analysis, identify_anomalies
from difflib import SequenceMatcher
import requests
from difflib import HtmlDiff
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class DocumentAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_text(self, txt_path):
        """
        Extract text from a plain text (.txt) file at the given path
        """
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
        
    def extract_text_from_documents(self):
        """
        Extract text from network logs
        """
        try:
            log_text=self.extract_text(self.file_path)
            return log_text

        except Exception as e:
            raise CustomException("Failed to extract data", e)
    
    def format_log(self, row):
        """
        Format a single log entry for better readability
        """
        try:
            return (
                f"[{row['timestamp']}] ({row['log_type']}, {row['event_type']}) "
                f"Severity: {row['severity']} | "
                f"{row['event_type']} from {row['source_ip']} to {row['destination_ip']} "
                f"using user '{row['user']}'. Message: {row['message']}"
            )
        except Exception as e:
            raise CustomException("Failed to format log entry", e)  

    def get_information_from_datasets(self):
        """
        Get information from datasets
        """
        try:
            df=pd.read_csv(self.file_path)
            df['formatted_log'] = df.apply(self.format_log, axis=1)
            return "\n".join(df['formatted_log'].tolist())
        except Exception as e:
            raise CustomException("Failed to read CSV file", e)


    def analyse_logs(self, logs):
        """
        Analyzes changes using llama 3.1
        
        Args:
            logs: String consisting network logs

        Output:
            string: Analysis of network logs
        """
        prompt = logs_analysis(logs)
        
        response = requests.post('http://localhost:11434/api/generate',
                                json={
                                    'model': 'llama3.1:8b-instruct-q4_K_M',
                                    'prompt': prompt,
                                    'stream': False
                                })
        
        return response.json()['response']
    
    def identify_anomalies(self, logs_analysis):
        """        
        Identifies anomalies in the logs analysis using llama 3.1
        """
        prompt = identify_anomalies(logs_analysis)

        response = requests.post('http://localhost:11434/api/generate',
                                json={
                                    'model': 'llama3.1:8b-instruct-q4_K_M',
                                    'prompt': prompt,
                                    'stream': False
                                })

        return response.json()['response']

    def run(self):
        try:
            logs= self.get_information_from_datasets()
            logs_analysis_result = self.analyse_logs(logs)
            anomalies = self.identify_anomalies(logs_analysis_result)
            return {
                "logs_analysis": logs_analysis_result,
                "anomalies": anomalies
            }
        
        except Exception as e:
            raise CustomException("Failed to extract and process logs", e)
