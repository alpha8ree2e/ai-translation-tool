import gradio as gr
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LANGUAGES = [
    "🇺🇸 English (US)", "🇬🇧 English (UK)", "🇨🇳 Chinese", "🇪🇸 Spanish",
    "🇫🇷 French", "🇸🇦 Arabic", "🇷🇺 Russian", "🇯🇵 Japanese", "🇰🇷 Korean"
]

STYLE_OPTIONS = ["--",
    "academic (used in papers)", "business (emails, formal)",
    "casual (friendly talk)", "social media (emoji & slang)",
    "poetic (figurative, expressive)", "fairytale (child-friendly)",
    "humor (funny or sarcastic)", "concise (brief and direct)"
]

SCENARIO_OPTIONS = ["--",
    "at a restaurant", "at an airport", "during a job interview", "on a business call",
    "at school", "asking for directions", "online shopping", "attending a meeting",
    "at a hospital", "making a hotel reservation", "socializing at a party"
]

EMOTION_OPTIONS = ["--",
    "neutral", "polite", "urgent", "friendly", "excited", "sad",
    "apologetic", "thankful / appreciative", "assertive", "persuasive", "confused"
]

PERSONAS = ["--",
    "student", "teacher", "professor", "child", "adult", "customer", "support agent",
    "subordinate", "boss", "colleague", "HR", "tourist", "local", "parent",
    "doctor", "patient", "intern", "executive"
]

def valid(value):
    return value and value.strip() and value != "--"

def build_prompt(text, source_lang, target_lang, from_persona, to_persona, style, scenario, emotion):
    parts = [
        f"Translate the following text from {source_lang} to {target_lang}.",
    ]
    if valid(style): parts.append(f"Style: {style};")
    if valid(scenario): parts.append(f"Scenario: {scenario};")
    if valid(emotion): parts.append(f"Emotion: {emotion};")
    if valid(from_persona): parts.append(f"From persona: {from_persona};")
    if valid(to_persona): parts.append(f"To persona: {to_persona};")
    parts.append("\nText:")
    parts.append(f"\"\"\"{text}\"\"\"")
    return "\n".join(parts)
    
def route_and_translate(
    text, source_lang, target_lang,
    from_dropdown, from_input,
    to_dropdown, to_input,
    style_dropdown, style_input,
    scenario_dropdown, scenario_input,
    emotion_dropdown, emotion_input
):
    from_persona = from_input.strip() if valid(from_input) else from_dropdown
    to_persona = to_input.strip() if valid(to_input) else to_dropdown
    style = style_input.strip() if valid(style_input) else style_dropdown
    scenario = scenario_input.strip() if valid(scenario_input) else scenario_dropdown
    emotion = emotion_input.strip() if valid(emotion_input) else emotion_dropdown
    prompt = build_prompt(text, source_lang, target_lang, from_persona, to_persona, style, scenario, emotion)
    system = "\n".join(["You are a professional translator specializing in accurately translating real-world conversations, ",
                        "including informal, vulgar, or emotionally charged language. Do not censor or paraphrase the content. " ,
                        "Translate the text faithfully and precisely, preserving slang, tone, intent, and formatting where applicable. ",
                        "Even if it includes slang, profanity, or offensive expressions. ",
                        "If style demands (e.g., email, formal), structure as email(don't forget subject and and closing signature). "
                       ])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

with gr.Blocks(title="AI Translation Tool") as demo:
    gr.Markdown("<h2 style='text-align: center;'>🌍 AI Translation Tool</h2>")

    input_text = gr.Textbox(label="Source Text", placeholder="Enter text to translate", lines=4)
    with gr.Row():
        source_lang = gr.Dropdown(LANGUAGES, label="Source Language", interactive=True)
        target_lang = gr.Dropdown(LANGUAGES, label="Target Language", interactive=True)
            
    translate_button = gr.Button("Translate", variant="primary", scale=2)
    mode = gr.Radio(["Select from Menu", "Write Your Own"], label="Choose Mode for Optional Settings", value="Select from Menu")
    
    with gr.Row():
        with gr.Column():
            from_dropdown = gr.Dropdown(PERSONAS, label="From Persona(optional)", visible=True, interactive=True)
            from_input = gr.Textbox(label="From Persona(optional)", visible=False, interactive=True)
        with gr.Column():
            to_dropdown = gr.Dropdown(PERSONAS, label="To Persona(optional)", visible=True, interactive=True)
            to_input = gr.Textbox(label="To Persona(optional)", visible=False, interactive=True)

    with gr.Row():
        with gr.Column():
            style_dropdown = gr.Dropdown(STYLE_OPTIONS, label="Style(optional)", visible=True, interactive=True)
            style_input = gr.Textbox(label="Style(optional)", visible=False, interactive=True)
        with gr.Column():
            scenario_dropdown = gr.Dropdown(SCENARIO_OPTIONS, label="Scenario(optional)", visible=True, interactive=True)
            scenario_input = gr.Textbox(label="Scenario(optional)", visible=False, interactive=True)
        with gr.Column():
            emotion_dropdown = gr.Dropdown(EMOTION_OPTIONS, label="Emotion(optional)", visible=True, interactive=True)
            emotion_input = gr.Textbox(label="Emotion(optional)", visible=False, interactive=True)

    result = gr.Textbox(label="Translation Result", lines=6)

    def update_mode(selected_mode):
        show = selected_mode == "Select from Menu"
        return (
            gr.update(visible=show), gr.update(visible=show),
            gr.update(visible=not show), gr.update(visible=not show),
            gr.update(visible=show), gr.update(visible=not show),
            gr.update(visible=show), gr.update(visible=not show),
            gr.update(visible=show), gr.update(visible=not show),
        )

    mode.change(
        update_mode,
        inputs=[mode],
        outputs=[
            from_dropdown, to_dropdown,
            from_input, to_input,
            style_dropdown, style_input,
            scenario_dropdown, scenario_input,
            emotion_dropdown, emotion_input
        ]
)

    translate_button.click(
        fn=route_and_translate,
        inputs=[
            input_text, source_lang, target_lang,
            from_dropdown, from_input,
            to_dropdown, to_input,
            style_dropdown, style_input,
            scenario_dropdown, scenario_input,
            emotion_dropdown, emotion_input
        ],
        outputs=result
    )
    
demo.launch()