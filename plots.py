# create_complete_performance_plot.py
import pandas as pd
import plotly.graph_objects as go
import os

# Create output directory
os.makedirs('docs', exist_ok=True)

# Read existing benchmark data
df = pd.read_csv('cipres/benchmark.csv')

# Calculate average unique sites
df['unique_sites_avg'] = (df['unique_sites_per_partition_min'] + df['unique_sites_per_partition_max']) / 2

# Filter out native kernel to focus on beagle_SSE performance
df_beagle = df[df['kernel'] == 'beagle_SSE'].copy()

print(f"Found {len(df_beagle)} beagle_SSE experiments")
print(f"Datasets: {df_beagle['dataset'].unique()}")
print(f"Core counts: {sorted(df_beagle['cores'].unique())}")

# Create the plot
fig = go.Figure()

# Color palette for different datasets
colors = {
    'Benchmark1': '#1f77b4',
    'Benchmark2': '#ff7f0e', 
    'DS3': '#2ca02c',
    'DS4': '#d62728',
    'DS5': '#9467bd',
    'DS6': '#8c564b',
    'DS7': '#e377c2'
}

# Add a trace for each dataset
for dataset in df_beagle['dataset'].unique():
    dataset_data = df_beagle[df_beagle['dataset'] == dataset]
    
    # Scale marker size based on cores (min size 8, max size 30)
    marker_sizes = 8 + (dataset_data['cores'] / dataset_data['cores'].max() * 22)
    
    fig.add_trace(go.Scatter(
        x=dataset_data['unique_sites_avg'],
        y=dataset_data['run_time_min'],
        mode='markers',
        name=dataset,
        marker=dict(
            size=marker_sizes,
            color=colors.get(dataset, 'gray'),
            line=dict(width=1, color='black'),
            opacity=0.7
        ),
        text=[f"{cores} cores" for cores in dataset_data['cores']],
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Unique sites/partition: %{x:.0f}<br>' +
                      'Run time: %{y:.2f} min<br>' +
                      'Cores: %{text}<br>' +
                      'Speedup: %{customdata[0]:.2f}x<br>' +
                      'Cost: %{customdata[1]:.1f} cpu-min<br>' +
                      'Config: %{customdata[2]}B/%{customdata[3]}T threads<extra></extra>',
        customdata=dataset_data[['speedup', 'cost_cpu_min', 'beast_threads', 'beagle_threads']].values
    ))

# Highlight 8-core configurations
df_8cores = df_beagle[df_beagle['cores'] == 8]
fig.add_trace(go.Scatter(
    x=df_8cores['unique_sites_avg'],
    y=df_8cores['run_time_min'],
    mode='markers',
    name='8-core (optimal)',
    marker=dict(
        size=15,
        symbol='star',
        color='gold',
        line=dict(width=2, color='black')
    ),
    showlegend=True,
    hovertemplate='<b>OPTIMAL 8-CORE</b><br>' +
                  'Dataset: %{text}<br>' +
                  'Unique sites/partition: %{x:.0f}<br>' +
                  'Run time: %{y:.2f} min<br>' +
                  'Speedup: %{customdata[0]:.2f}x<extra></extra>',
    text=df_8cores['dataset'],
    customdata=df_8cores[['speedup']].values
))

# Add size legend reference
size_legend_x = [100, 200, 400, 800]
size_legend_y = [0.5, 0.5, 0.5, 0.5]
size_legend_sizes = [8, 16, 24, 30]
size_legend_text = ['1 core', '8 cores', '16 cores', '32 cores']

fig.add_trace(go.Scatter(
    x=size_legend_x,
    y=size_legend_y,
    mode='markers+text',
    name='Core count',
    marker=dict(
        size=size_legend_sizes,
        color='lightgray',
        line=dict(width=1, color='black')
    ),
    text=size_legend_text,
    textposition='top center',
    showlegend=False,
    hoverinfo='skip'
))

# Add annotation for size legend
fig.add_annotation(
    x=300,
    y=0.35,
    text="Marker size = Core count",
    showarrow=False,
    font=dict(size=10, color='gray')
)

fig.update_layout(
    title={
        'text': 'BEAST/BEAGLE Performance: Sites per Partition vs Runtime (All Configurations)',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis=dict(
        title='Average Unique Sites per Partition',
        type='log',
        gridcolor='lightgray',
        showgrid=True,
        zeroline=False,
        range=[1.3, 4]  # Adjust based on your data
    ),
    yaxis=dict(
        title='Run Time (minutes)',
        type='log',
        gridcolor='lightgray',
        showgrid=True,
        zeroline=False,
        range=[-0.5, 2.5]  # Adjust based on your data
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='closest',
    width=1200,
    height=800,
    font=dict(family="Arial", size=12),
    legend=dict(
        x=0.02,
        y=0.98,
        xanchor='left',
        yanchor='top',
        bgcolor='rgba(255, 255, 255, 0.9)',
        bordercolor='black',
        borderwidth=1
    )
)

# Save the plot
fig.write_html('docs/sites_vs_runtime_all_cores.html')

# Create a summary statistics table
summary_stats = df_beagle.groupby(['dataset', 'cores']).agg({
    'unique_sites_avg': 'first',
    'run_time_min': 'first',
    'speedup': 'first',
    'cost_cpu_min': 'first',
    'partitions': 'first'
}).round(2)

print("\nSummary by dataset and cores:")
print(summary_stats.head(15))

# Save all beagle_SSE data for reference
df_beagle.to_csv('docs/all_beagle_experiments_data.csv', index=False)

# Create a simple index.html
index_html = """<!DOCTYPE html>
<html>
<head>
    <title>BEAST-BEAGLE Performance Analysis</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 { color: #333; text-align: center; }
        h2 { color: #555; margin-top: 30px; }
        .plot-description {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .insight {
            background-color: #e9ecef;
            padding: 10px 15px;
            border-left: 4px solid #007bff;
            margin: 10px 0;
        }
        ul { line-height: 1.8; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>BEAST-BEAGLE Performance Analysis</h1>
        
        <div class="plot-description">
            <h2>Performance Visualization</h2>
            <p>This interactive plot shows the relationship between dataset complexity (unique sites per partition) 
            and runtime for different core configurations. Marker size indicates the number of cores used.</p>
            <ul>
                <li>⭐ Star markers highlight the optimal 8-core configurations</li>
                <li>Larger circles indicate more cores (1 to 32)</li>
                <li>Each color represents a different dataset</li>
                <li>Hover over points for detailed performance metrics</li>
            </ul>
        </div>

        <h2>Interactive Plot</h2>
        <p><a href="sites_vs_runtime_all_cores.html">📊 View Performance Analysis (All Core Configurations)</a></p>
        
        <div class="insight">
            <strong>Key Insight:</strong> The 8-core configuration (gold stars) provides the best balance 
            between performance and computational cost across all datasets.
        </div>
        
        <h2>Data Download</h2>
        <ul>
            <li><a href="all_beagle_experiments_data.csv">📥 Download complete experiment data (CSV)</a></li>
        </ul>
        
        <h2>Repository</h2>
        <p>View the complete analysis and source code on <a href="https://github.com/CamilaDuitama/BEAST-BEAGLE-Performance-Analysis">GitHub</a></p>
    </div>
</body>
</html>"""

with open('docs/index.html', 'w') as f:
    f.write(index_html)

print(f"\nFiles created:")
print(f"  - docs/sites_vs_runtime_all_cores.html (main plot)")
print(f"  - docs/all_beagle_experiments_data.csv (data)")
print(f"  - docs/index.html (landing page)")
print(f"\nPush to GitHub and enable Pages to view at:")
print(f"https://camiladuitama.github.io/BEAST-BEAGLE-Performance-Analysis/")
