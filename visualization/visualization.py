import pandas as pd
import folium
from folium.plugins import MarkerCluster
import altair as alt

# --- Load data ---
data = pd.read_csv('result.csv')

# --- Create Folium Map ---
m = folium.Map(location=[59.3293, 18.0686], zoom_start=6, tiles="OpenStreetMap")
marker_cluster = MarkerCluster().add_to(m)
for _, row in data.iterrows():
    folium.Marker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        popup=(f"<b>Municipality:</b> {row['MUNICIPALITY']}<br>"
               f"<b>District:</b> {row['DISTRICT']}<br>"
               f"<b>Rent:</b> {row['RENT']} SEK<br>"
               f"<b>Rooms:</b> {row['ROOMS']}<br>"
               f"<b>Floor Area:</b> {row['FLOOR_AREA']} m²"),
    ).add_to(marker_cluster)
map_html = m._repr_html_()

# --- Bar Chart ---
data['PUBLISHED'] = pd.to_datetime(data['PUBLISHED'])
daily_counts = data.groupby('PUBLISHED').size().reset_index(name='COUNT')

bar_chart = alt.Chart(daily_counts).mark_bar(size=30).encode(
    x=alt.X('PUBLISHED:T', title='Publication Date'),
    y=alt.Y('COUNT:Q', title='Number of Advertised Apartments'),
    color=alt.Color('COUNT:Q', scale=alt.Scale(scheme='blues')),
    tooltip=['PUBLISHED:T', 'COUNT:Q']
).properties(
    width=600,
    height=300,
    title="Apartments Published Per Day"
)

# --- Summary Cards ---
avg_data = pd.DataFrame({
    'Category': ['Rent', 'Number of Rooms', 'Floor Area'],
    'Average': [
        round(data['RENT'].mean(), 2),
        round(data['ROOMS'].mean(), 2),
        round(data['FLOOR_AREA'].mean(), 2)
    ],
    'Unit': ['SEK', '', 'm²']
})

charts = []
for index, row in avg_data.iterrows():
    card = alt.Chart(pd.DataFrame([row])).mark_bar(
        size=200,
        cornerRadiusTopLeft=10,
        cornerRadiusTopRight=10
    ).encode(
        y=alt.Y('Category:N', title=None, axis=None),
        x=alt.X('Average:Q', title=None, axis=None),
        color=alt.Color('Category:N', scale=alt.Scale(scheme='category10'), legend=None),
        tooltip=[
            alt.Tooltip('Category:N', title='Category'),
            alt.Tooltip('Average:Q', title='Average', format='.2f'),
            alt.Tooltip('Unit:N', title='Unit')
        ]
    ).properties(
        width=200,
        height=300
    )

    value_text = alt.Chart(pd.DataFrame([row])).mark_text(
        align='center',
        baseline='middle',
        fontSize=18,
        color='white'
    ).encode(
        y=alt.value(150),
        text=alt.Text('Average:Q', format='.2f')
    )

    category_text = alt.Chart(pd.DataFrame([row])).mark_text(
        align='center',
        baseline='top',
        fontSize=14,
        color='black'
    ).encode(
        y=alt.value(320),
        text=alt.Text('Category:N')
    )

    charts.append(card + value_text + category_text)

cards_chart = alt.hconcat(*charts).properties(
    title="Average Rent, Number of Rooms, and Floor Area"
)

# --- Pie Chart ---
lease_counts = data.groupby('LEASE_TYPE').size().reset_index(name='COUNT')
lease_counts['PERCENT'] = (lease_counts['COUNT'] / lease_counts['COUNT'].sum()) * 100
pie_chart = alt.Chart(lease_counts).mark_arc(innerRadius=50).encode(
    theta=alt.Theta('PERCENT:Q', title='Percentage'),
    color=alt.Color('LEASE_TYPE:N', title='Lease Type'),
    tooltip=['LEASE_TYPE:N', 'PERCENT:Q', 'COUNT:Q']
).properties(
    title="Lease Type Distribution",
    width=600,
    height=300
)

# Combine Charts Without Title
altair_combined = alt.vconcat(
    bar_chart,
    pie_chart,
    cards_chart
).configure_title(
    fontSize=18,
    anchor='start',
    font='Arial'
).configure_view(
    strokeOpacity=0
)

altair_html = altair_combined.to_html()

# --- Combine Everything into a Single HTML ---
final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Visualizations</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        section {{
            margin-bottom: 40px;
        }}
    </style>
</head>
<body>
    <section>
        <h1>Available Apartments</h1>
        {map_html}
    </section>
    {altair_html}
</body>
</html>
"""

# Save the Final HTML File
with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(final_html)


