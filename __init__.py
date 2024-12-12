from transformers import pipeline

# Load a pre-trained model for paraphrasing
paraphrase_pipeline = pipeline("text2text-generation", model="Vamsi/T5_Paraphrase_Paws")

def rephrase_text(text):
    # Use the model to generate a paraphrased version of the text
    rephrased_text = paraphrase_pipeline(text, max_length=512, num_return_sequences=1)[0]['generated_text']
    return rephrased_text

# Example usage
input_text = "I want to learn how to use Python for data processing"
rephrased_text = rephrase_text(input_text)
print("Original Text: ", input_text)
print("Rephrased Text: ", rephrased_text)
