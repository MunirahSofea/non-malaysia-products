import pandas as pd
import io
import requests
from flask import Flask, render_template, request, redirect, url_for
import plotly.express as px
import numpy as np

app = Flask(__name__, template_folder="C:/Users/Munirah Sofea/Downloads/templates")

compiled_drive_link ='https://drive.google.com/uc?id=1jWGU24KtO7f_t3PqJauYaNVVVyn44whc'
def load_compiled():
    download_url =f'https://drive.google.com/uc?id=1jWGU24KtO7f_t3PqJauYaNVVVyn44whc'
    response = requests.get(download_url)
    content = io.BytesIO(response.content)
    compiled = pd.read_excel("compiled.xlsx")
    return compiled

@app.route('/')
def index():
    compiled = load_compiled()
    country_list = compiled['country'].unique()
    print("DEBUG: Country List →", country_list) 
    return render_template("index.html", country=country_list) 


@app.route('/visualization', methods=['POST', 'GET'])
def visualization():
    compiled = load_compiled()
    
    # Get selected countries from form
    selected_countries = request.form.getlist('country')
    
    if not selected_countries:
        return render_template("visualization.html", country=compiled['country'].unique(), message="Please select at least one country.")
    
    # Filter data for selected countries
    selected_countries_data = compiled[compiled['country'].isin(selected_countries)]
    
    # Create visualizations
    fig_quantity_rate = px.line(
        selected_countries_data, x='Year', y='Quantity', color='country', title='Quantity Over Time'
    )
    fig_value_rate = px.line(
        selected_countries_data, x='Year', y='Value', color='country', title='Value Over Time'
    )
    fig_product_rate = px.line(
        selected_countries_data, x='Year', y='Product', color='country', title='Product Over Time'
    )
    
    # Update layouts for dark theme
    layout_updates = {
        "paper_bgcolor": "#a11597",
        "font": dict(color="#FFFFFF"),
        "xaxis": dict(
            rangeslider=dict(visible=True)
        ),
    }

    fig_quantity_rate.update_layout(**layout_updates)
    fig_value_rate.update_layout(**layout_updates)
    fig_product_rate.update_layout(**layout_updates)

    return render_template(
        "visualization.html",
        fig_quantity_rate=fig_quantity_rate.to_html(full_html=False),
        fig_value_rate=fig_value_rate.to_html(full_html=False),
        fig_product_rate=fig_product_rate.to_html(full_html=False),
        selected_countries=selected_countries,
    )
    
@app.route('/scatter', methods=['GET', 'POST']) 
def scatter():
        selected_countries = request.args.get('country').split(",") 
        compiled = load_compiled()
        selected_countries_data = compiled[compiled['country'].isin(selected_countries)]

        fig_quantity_rate_scatter = px.scatter(selected_countries_data, x='Year', y='Quantity', color='country', title='Quantity Over Time') 
        fig_value_rate_scatter = px.scatter(selected_countries_data, x='Year', y='Value', color='country', title='Value Over Time')
        fig_product_rate_scatter = px.scatter(selected_countries_data, x='Year', y='Product', color='country', title='Product Over Time')
    
        fig_quantity_rate_scatter.update_layout(
                paper_bgcolor="#a11597",
                font = dict(color="#FFFFFF"),
                xaxis=dict(
                    rangeselector=dict( 
                        buttons=list([
                            dict(count=1, 
                                 step="day", 
                                 stepmode="backward"),
                        ])
                    ),
                    rangeslider=dict(
                          visible=True
                    ),
                )
            )
        
        fig_value_rate_scatter.update_layout(
                paper_bgcolor="#a11597",
                font=dict(color="#FFFFFF"), 
                xaxis=dict(
                    rangeselector=dict( 
                        buttons=list([
                            dict(count=1,
                                step="day",
                                stepmode="backward"),
                        ])
                    ),
                    rangeslider=dict(
                          visible=True
                    ),
                )
            )

        fig_product_rate_scatter.update_layout( 
                paper_bgcolor="#a11597",
                font=dict(color="#FFFFFF"), 
                xaxis=dict(
                    rangeselector=dict( 
                        buttons=list([
                            dict(count=1,
                                step="day",
                                stepmode="backward"),
                        ])
                    ),
                    rangeslider=dict(
                          visible=True
                    ),
                )
             )

        return render_template(
            "scatter.html",
            fig_quantity_rate_scatter=fig_quantity_rate_scatter.to_html(full_html=False), 
            fig_value_rate_scatter=fig_value_rate_scatter.to_html(full_html=False), 
            fig_product_rate_scatter=fig_product_rate_scatter.to_html(full_html=False), 
            selected_countries=selected_countries,
            compiled=compiled,
        )
def calculate_growth_percentage(initial, final):
    """Calculate the percentage growth between two values."""
    if initial == 0:
        return 0  # Avoid division by zero
    return ((final - initial) / initial) * 100

@app.route('/analysis', methods=["GET"])
def analysis():
    selected_countries = request.args.get('country', '').split(',')
    compiled = load_compiled()
    
    selected_countries_data = compiled[compiled['country'].isin(selected_countries)]
    
    # Calculate percentage growth rates
    quantity_growth_rates = []
    for country in selected_countries:
        country_data = selected_countries_data[selected_countries_data['country'] == country]
        
        quantity_2017 = country_data.loc[country_data['Year'] == 2017, "Quantity"]
        quantity_2022 = country_data.loc[country_data['Year'] == 2022, "Quantity"]
        
        if not quantity_2017.empty and not quantity_2022.empty:
            quantity_2017 = quantity_2017.iloc[0]
            quantity_2022 = quantity_2022.iloc[0]
            
            growth_percentage = calculate_growth_percentage(quantity_2017, quantity_2022)
            
            quantity_growth_rates.append((country, growth_percentage))

    return render_template(
        'analysis.html',
        selected_countries=selected_countries,
        quantity_growth_rates=quantity_growth_rates
    )

if __name__ == "__main__":
    app.run(debug=True)