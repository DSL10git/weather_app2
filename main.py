from __future__ import annotations
import gradio as gr
import openai
import requests
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from typing import Iterable
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes

with open("keys.json") as f:
    keys = json.load(f)


def toggle_popup(is_visible):
    return not is_visible, gr.update(visible=not is_visible)


def feedback(feedback):
    if feedback == "Y" or feedback == "y" or feedback == "Yes" or feedback == "yes":
        return "Thank you for your feedback, click flag as like!"
    elif feedback == "N" or feedback == "n" or feedback == "No" or feedback == "no":
        return "Thank you for your feedback, click flag as dislike!"
    else:
        return "Please enter Y or Yes or N or No"


def recommendations(city, users_state):
    # Check login
    if not users_state:
        return "Error: User state is not initialized. Please log in first!"
    logged_users = users_state.get('logged_users', set())
    if len(logged_users) == 0:
        return "No users, please log in first!"

    # Get weather info
    api_key = keys["weather_key"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        messages = [{"role": "system", "content": "you are chatgpt"}]
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        openai.api_key = keys["openai_key"]
        messages.append(
            {
                "role": "user",
                "content":
    f"""
    Can you give me some recommendations for {address(city)}?
    It the weather description is {desc} and the temperature is {temp}°K
    Please answer with a short paragraph
    """,
            }
        )
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages
        )
        ChatGPT_reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ChatGPT_reply})

        # return new_visible as well
        # update label of textbox
        # something like gr.update(value=label)
        return ChatGPT_reply
    else:
        return "city not found"


def toggle_visibility(is_visible):
    if is_visible:
        label = "Show more"
    else:
        label = "Hide"
    new_visible = not is_visible
    return (
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(visible=new_visible),
        gr.update(value=label),
        new_visible
    )


def address(city):
    api_key = keys["weather_key"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    latitude = data["coord"]["lat"]
    longitude = data["coord"]["lon"]
    address = get_address_from_coordinates(latitude, longitude)
    address = f"Address: {address}"
    return address


def get_address_from_coordinates(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        data = response.json()
        if "address" in data:
            return data["display_name"]
        else:
            return "No address found for these coordinates."
    else:
        return f"HTTP Error: {response.status_code}"


def temp(city, unit):
    return f"Temperature in {city} is {display_weather(city, unit)[0]}"


def get_weather(city, unit, w_unit):
    print(city, unit, w_unit)
    api_key = keys["weather_key"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_desc = data["weather"][0]["description"]
        weather_temp = data["main"]["temp"]
        weather_id = data["weather"][0]["id"]
        return display_weather(city, unit)[0], display_weather(city, unit)[1], weather_desc, feels_like2(city, unit), wind(city, w_unit), address(city)
    else:
        return "City not found", "City not found", "City not found", "City not found", "City not found", "City not found"


def feels_like2(city, unit):
    api_key = keys["weather_key"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}" 
    response = requests.get(url)
    data = response.json()
    more_info = ""
    feels_like_k = data["main"]["feels_like"]
    if unit == "Celsius":
        feels_like = feels_like_k - 273.15
        more_info += f"Feels like: {feels_like:.1f} °C"
    elif unit == "Fahrenheit":
        feels_like = (feels_like_k * 9/5) - 459.67
        more_info += f"Feels like: {feels_like:.0f} °F"
    elif unit == "Kelvin":
        more_info += f"Feels like: {feels_like_k:.0f} °K"
    else:
        temp_display = "N/A"
    return more_info


def wind(city, w_unit):
    api_key = keys["weather_key"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    wind_speed = data["wind"]["speed"]
    if response.status_code == 200:
        wind = ""
        # Get Wind speed
        if w_unit == "MPH":
            wind_speed = wind_speed * 2.23694  # Convert m/s to mph
            wind += f"\nWind speed: {wind_speed:.1f} mph"
        elif w_unit == "KM/H":
            wind_speed = wind_speed * 3.6  # Convert m/s to km/h
            wind += f"\nWind speed: {wind_speed:.1f} km/h"
            return wind
        wind_speed = data["wind"]["speed"]
        # Get Feels Like
    else:
       wind += "N/A"
    return wind

  
class Seafoam(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.emerald,
        secondary_hue: colors.Color | str = colors.blue,
        neutral_hue: colors.Color | str = colors.blue,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_md,
        text_size: sizes.Size | str = sizes.text_lg,
        font: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Quicksand"),
            "ui-sans-serif",
            "sans-serif",
        ),
        font_mono: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("IBM Plex Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )
        super().set(
            body_background_fill="repeating-linear-gradient(45deg, *primary_200, *primary_200 10px, *primary_50 10px, *primary_50 20px)",
            body_background_fill_dark="repeating-linear-gradient(45deg, *primary_800, *primary_800 10px, *primary_900 10px, *primary_900 20px)",
            button_primary_background_fill="linear-gradient(90deg, *primary_300, *secondary_400)",
            button_secondary_background_fill="linear-gradient(90deg, *primary_300, *secondary_400)",
            button_primary_background_fill_hover="linear-gradient(90deg, *primary_200, *secondary_300)",
            button_secondary_background_fill_hover="linear-gradient(90deg, *primary_200, *secondary_300)",
            button_primary_text_color="white",
            button_secondary_text_color="white",
            button_primary_background_fill_dark="linear-gradient(90deg, *primary_600, *secondary_800)",
            button_secondary_background_fill_dark="linear-gradient(90deg, *primary_600, *secondary_800)",
            slider_color="*secondary_300",
            slider_color_dark="*secondary_600",
            block_title_text_weight="600",
            block_border_width="3px",
            block_shadow="*shadow_drop_lg",
            button_primary_shadow="*shadow_drop_lg",
            button_secondary_shadow="*shadow_drop_lg",
            button_large_padding="32px",
        )


seafoam = Seafoam()


def login(username, password, users_state):
    users = users_state['users']
    logged_users = users_state['logged_users']

    if username in users:
        if password == users[username]:
            logged_users.add(username)
            message = "user logged in successfully"
        else:
            message = "password doesn't match"
    else:
        message = "user isn't in the system"

    gr.Info(message)
    return users_state


def get_weather_emoji(weather_id):
    if 200 <= weather_id <= 232:
        return "⛈️"
    elif 300 <= weather_id <= 321:
        return "⛆"
    elif 500 <= weather_id <= 531:
        return "🌧️"
    elif 500 <= weather_id <= 622:
        return "❄️"
    elif 701 <= weather_id <= 741:
        return "🌫️"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "💨"
    elif weather_id == 781:
        return "🌪️"
    elif weather_id == 800:
        return "☀️"
    elif 801 <= weather_id <= 804:
        return "☁️"
    else:
        return "🌍"  # Default emoji
def display_weather(city, unit):
    api_key = keys["weather_key"]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}" 
    response = requests.get(url)
    if response.status_code != 200:
        return "City not found", "", ""
    
    data = response.json()
    temperature_k = data["main"]["temp"]
    weather_id = data["weather"][0]["id"]
    weather_description = data["weather"][0]["description"]
    
    if unit == "Celsius":
        temperature = temperature_k - 273.15
        temp_display = f"{temperature:.1f} °C"
    elif unit == "Fahrenheit":
        temperature = (temperature_k * 9/5) - 459.67
        temp_display = f"{temperature:.1f} °F"
    elif unit == "Kelvin":
        temp_display = f"{temperature_k:.1f} K"
    else:
        temp_display = "N/A"
    
    return temp_display, get_weather_emoji(weather_id), weather_description


demo_css = """
body {
    background-image: url("sunny_cartoon_backgound.webp");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
.gradio-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100vh;
    padding-top: 20px;
}
.recommendation-container {
    display: flex;
    align-items: center;
    margin-top: 10px;
}
.recommendation-image {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    margin-left: 10px;
"""
with gr.Blocks(css=demo_css, theme=seafoam) as demo:
    with gr.Row():
        about_btn = gr.Button("About", scale=0)
        title = gr.HTML("""
            <h1 style="text-align:center"> Weather App 2! By Daniel</h1>
        """)
    # Hidden popup text
    popup = gr.Markdown(
        value="""Weather App 2!         By Daniel
    1. place Input
    You can type the name of any place in a text
    input box to fetch its weather information.
                        
    2. Unit Selection                    
    This app allows you to view the temperature in Celsius, Fahrenheit, or Kelvin using radio buttons.  
                        
    3. Weather Information
    Displays:
        Temperature in the selected unit.
        Weather Description (e.g., sunny, cloudy, rainy, etc.).
        emoji-based weather icons.
                        
    4. Error Handling    
    Handles common API and connection errors, such as:
        City not found
        Invalid API key
        Server errors
        Internet connectivity issues
        Displays user-friendly error messages for each type of error.
            
    5. Responsive Design   
    The app dynamically adjusts the position of elements like the "About the Website" button based on the size of the window.

    6. Reccomendation
    This app can tell you what to wear, bring, and etc based on the weather, description, wind, and etc

    How To Use
    Type in a zip code (e.g 12345), contry(e.g Russia), county(e.g Los angles), city(e.g Unalaska), and ect 
    It will give you the temperature(You can pick between K(Kelvin), F(fahrenheit), or C(celsius) KFC!), rain and ect, and weather emoji.
    If you click Show more it will give you the wind (You can pick between Mph or Km/h), what it feels like, and place(road, city, county, state, zip code, and contry)!                                  """,
        visible=False,
    )
    place = gr.Textbox(placeholder="Enter a place!")
    weather_btn = gr.Button("Get weather")
    unit = gr.Radio(["Kelvin", "Fahrenheit", "Celsius"], label="Temperature", info="Select a temperature unit(KFC)!", value="Kelvin")
    temp_display = gr.Textbox(label="Temperature")
    emoji_display = gr.Textbox(label="Weather Emoji")
    description_display = gr.Textbox(label="Description")
    """
    btn.click(
        wind, 
        inputs=[
            place,
            w_unit
        ],
        outputs=wind_speed
    )
    """
    # Outputs for temperature, weather emoji, and description
    #########################################################################
    show_more_btn = gr.Button("Show More")
    w_unit = gr.Radio(["MPH", "KM/H"], label="Wind Speed", info="Select a wind Speed!", value="MPH", visible=False)
    feels_like = gr.Textbox(label="Feels Like", visible=False)
    wind_speed = gr.Textbox(label="Wind Speed", visible=False)
    address_n = gr.Textbox(label="Address", visible=False)

    with gr.Column():
        username_txt = gr.Textbox(label="Username", type="text", visible=False)
        password_txt = gr.Textbox(label="Password", type="password", visible=False)
        login_btn = gr.Button("Login", visible=False)
        recommend_txt = gr.Textbox(label="Recommendation", visible=False)
        recommend_btn = gr.Button("Recommendation", visible=False)


    weather_btn.click(
        get_weather, # sentence_builder
        inputs=[
            place,
            unit,
            w_unit
        ],
        outputs=[
            temp_display,
            emoji_display,
            description_display,
            feels_like,
            wind_speed,
            address_n
        ]
    )
    
    show_visibility_state = gr.State(False)
    show_more_btn.click(
        toggle_visibility,
        inputs=[show_visibility_state],
        outputs=[
            w_unit, # hide/show, visible
            feels_like, # hide/show, visible
            wind_speed, # hide/show, visible
            address_n, # hide/show, visible
            username_txt,
            password_txt,
            login_btn,
            recommend_txt,
            recommend_btn,
            show_more_btn, # change label, value
            show_visibility_state
        ])

    users_state = gr.State({
        "users": keys["users"],
        "logged_users": set()
    })
    login_btn.click(
        login,
        inputs=[username_txt, password_txt, users_state],
        outputs=[users_state]
    )
    recommend_btn.click(
        recommendations,
        inputs=[place, users_state],
        outputs=[recommend_txt]
    )
    
    about_visibility_state = gr.State(False)
    about_btn.click(
        toggle_popup,
        inputs=[about_visibility_state],
        outputs=[about_visibility_state, popup]
    )
    flagging = gr.Interface(
        fn=feedback,
        inputs="text",  # Hidden input to satisfy Gradio's requirement
        outputs="text",  # Hidden output to satisfy Gradio's requirement
        live=False,  # Prevents triggering unnecessary updates
        flagging_options=["like", "dislike"]  # Only flagging options
    )
demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
