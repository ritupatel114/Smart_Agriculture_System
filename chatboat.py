def get_bot_response(message):

    message = message.lower()

    if "fertilizer" in message and "wheat" in message:
        return "For wheat, Urea and DAP are commonly recommended."

    elif "fertilizer" in message and "rice" in message:
        return "For rice, Urea and Potash are recommended."

    elif "yellow" in message and "leaf" in message:
        return "Yellow leaves may indicate nitrogen deficiency or disease. Upload a leaf image for AI diagnosis."

    elif "tomato" in message:
        return "Tomato grows best in well-drained loamy soil with regular watering."

    elif "cotton" in message:
        return "Cotton grows best in black soil during the Kharif season."

    elif "water" in message:
        return "Proper irrigation depends on the crop. Rice requires more water than wheat."

    elif "hello" in message or "hi" in message:
        return "Hello! I am your Smart Agriculture Assistant. How can I help you?"

    else:
        return "Sorry, I don't understand. Please ask about crops, fertilizer, irrigation, weather, or diseases."