def analyze_comment(comment):
    """
    Send a comment to ChatGPT and get scores for ranking, friendliness,
    general ratings, flexibility, ease, and affordability.
    """
    prompt = f"""
    Please rate the following comment on a scale of 1 to 5 for these categories:
    - Ranking (1 to 5)
    - Friendliness (1 to 5)
    - General rating (1 to 5)
    - Flexibility in scheduling (1 to 5)
    - Ease of scheduling (1 to 5)
    - Affordability (1 to 5)

    Respond with only the numbers for each category, one per line, or "0" if a category is not mentioned in the comment.

    Comment: "{comment}"
    """
    
    try:
        response = chat([HumanMessage(content=prompt)])
        scores = response.content.split('\n')
        
        # Convert scores to float, with non-numeric values set to 0
        processed_scores = {}
        for line in scores:
            if ':' in line:
                key, value = line.split(":", 1)
                value = value.strip()
                try:
                    processed_scores[key] = float(value)
                except ValueError:
                    processed_scores[key] = 0.0  # Set non-numeric to 0
        return processed_scores
    except Exception as e:
        print(f"Error parsing response: {e}")
        return {
            "Ranking": 0.0,
            "Friendliness": 0.0,
            "General Rating": 0.0,
            "Flexibility": 0.0,
            "Ease": 0.0,
            "Affordability": 0.0
        }
