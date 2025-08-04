#prompt_templates/templates.py
def default_chat_template(analysis):
    """
    set's up default LLM prompt for chatbot
    """
    default_system_prompt = f"""
    Act as a cybersecurity expert specializing in network logs analysis.
    You are provided with a detailed analysis of network logs.
    Your task is to assist users in understanding the analysis, identifying potential security threats, and providing recommendations for mitigation.
    If the user asks for anything unrelated to network logs analysis, politely inform them that you can only assist with network logs analysis.
    Here is the analysis:
    {analysis}
    Please provide a concise and informative response to user queries related to network logs analysis.
    """
    return default_system_prompt

def logs_analysis(logs):
    """
    Set up the logs analysis prompt template
    """
    return f"""
    You are an expert in analyzing network logs. Your task is to analyze the provided logs and identify any anomalies or issues.
    
    Logs:
    {logs}
    
    Create a short analysis of the logs.
    """

def identify_anomalies(logs_analysis):
    """
    Set up the prompt template for identifying anomalies in logs
    """
    return f"""
    You are an expert in cybersecurity. Your task is to identify anomalies in the provided network log analysis.
    
    logs_analysis:
    {logs_analysis}
    
    Create a short report identifying any anomalies and recommended actions.
    Structure the response using points.
    """