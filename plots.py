# create_sites_vs_runtime_plot.py
import pandas as pd
import plotly.graph_objects as go
import os

# Create output directory
os.makedirs('docs', exist_ok=True)

# Read existing benchmark data
df = pd.read_csv('cipres/benchmark.csv')

# Calculate average unique sites
df['unique_sites_avg'] = (df['unique_sites_per_partition_min'] + df['unique_sites_per_partition_max']) / 2

# Filter for 8-core experiments only
df_8cores = df[df['cores'] == 8].copy()

print(f"Found {len(df_8cores)} experiments with 8 cores")
print(f"Datasets: {df_8cores['dataset'].unique()}")

# Create the plot
fig = go.Figure()

# Add a trace for each dataset
colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']

for i, dataset in enumerate(df_8cores['dataset'].unique()):
    dataset_data = df_8cores[df_8cores['dataset'] == dataset]
    
    fig.add_trace(go.Scatter(
        x=dataset_data['unique_sites_avg'],
        y=dataset_data['run_time_min'],
        mode='markers+lines',
        name=dataset,
        marker=dict(
            size=12,
            color=colors[i % len(colors)],
            symbol='circle',
            line=dict(width=2, color='black')
        ),
        line=dict(
            color=colors[i % len(colors)],
            width=2,
            dash='solid'
        ),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Unique sites/partition: %{x:.0f}<br>' +
                      'Run time: %{y:.2f} min<br>' +
                      'Partitions: %{customdata[0]}<br>' +
                      'BEAST threads: %{customdata[1]}<br>' +
                      'BEAGLE threads: %{customdata[2]}<extra></extra>',
        customdata=dataset_data[['partitions', 'beast_threads', 'beagle_threads']].values
    ))

# Add annotations for key insights
fig.add_annotation(
    x=5565,
    y=1.84,
    text="Benchmark2<br>Best performance",
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="black",
    ax=50,
    ay=-40,
    font=dict(size=10)
)

fig.update_layout(
    title={
        'text': 'BEAST/BEAGLE Performance: Sites per Partition vs Runtime (8-core configuration)',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis=dict(
        title='Average Unique Sites per Partition',
        type='log',
        gridcolor='lightgray',
        showgrid=True,
        zeroline=False
    ),
    yaxis=dict(
        title='Run Time (minutes)',
        type='log',
        gridcolor='lightgray',
        showgrid=True,
        zeroline=False
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='closest',
    width=1000,
    height=700,
    font=dict(family="Arial", size=12),
    legend=dict(
        x=0.02,
        y=0.98,
        xanchor='left',
        yanchor='top',
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='black',
        borderwidth=1
    )
)

# Save the plot
fig.write_html('docs/sites_vs_runtime_8cores.html')

# Also create a simple summary table
summary = df_8cores.groupby('dataset').agg({
    'unique_sites_avg': 'first',
    'run_time_min': 'first',
    'partitions': 'first',
    'beast_threads': 'first',
    'beagle_threads': 'first',
    'speedup': 'first'
}).round(2)

print("\nSummary of 8-core experiments:")
print(summary.to_string())

# Save the plot data for reference
df_8cores.to_csv('docs/8core_experiments_data.csv', index=False)

print(f"\nPlot saved to: docs/sites_vs_runtime_8cores.html")
print(f"Data saved to: docs/8core_experiments_data.csv")
