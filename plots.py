# create_plots_with_native_kernel.py
import pandas as pd
import plotly.graph_objects as go
import os

# Create output directory
os.makedirs('docs', exist_ok=True)

# Read existing benchmark data
df = pd.read_csv('cipres/benchmark.csv')

# Calculate average unique sites per partition
df['unique_sites_avg'] = (df['unique_sites_per_partition_min'] + df['unique_sites_per_partition_max']) / 2

print(f"Kernels found: {df['kernel'].unique()}")

# Get unique partition counts
partition_counts = sorted(df['partitions'].unique())
print(f"Creating plots for partition counts: {partition_counts}")

# Color palette for different datasets
colors = {
    'Benchmark1': "#499ad4",
    'Benchmark2': "#f6a056", 
    'DS3': "#70C670",
    'DS4': "#c84a4a",
    'DS5': "#957eab",
    'DS6': "#f0d465",
    'DS7': "#df90c7"
}

# Define a list of plotly marker symbols to use for thread combos
symbol_list = [
    'circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down',
    'triangle-left', 'triangle-right', 'star', 'hexagram', 'bowtie'
]

# Build a mapping from (beast_threads, beagle_threads) to a symbol
thread_combos = sorted(set(zip(df['beast_threads'], df['beagle_threads'])))
combo_to_symbol = {combo: symbol_list[i % len(symbol_list)] for i, combo in enumerate(thread_combos)}

# Reverse mapping for legend
symbol_to_combo = {}
for combo, symbol in combo_to_symbol.items():
    symbol_to_combo.setdefault(symbol, []).append(combo)

# Create one plot for each partition count
for partition_count in partition_counts:
    partition_data = df[df['partitions'] == partition_count]
    if partition_data.empty:
        continue

    fig = go.Figure()

    if partition_count == 1:
        # One marker per trace: each trace is a unique (dataset, beast_threads, beagle_threads) combo
        unique_combos = partition_data[['dataset', 'beast_threads', 'beagle_threads']].drop_duplicates()
        for _, combo_row in unique_combos.iterrows():
            dataset = combo_row['dataset']
            beast_threads = combo_row['beast_threads']
            beagle_threads = combo_row['beagle_threads']
            symbol = combo_to_symbol[(beast_threads, beagle_threads)]
            color = colors.get(dataset, 'gray')
            combo_data = partition_data[
                (partition_data['dataset'] == dataset) &
                (partition_data['beast_threads'] == beast_threads) &
                (partition_data['beagle_threads'] == beagle_threads)
            ]
            if combo_data.empty:
                continue
            row = combo_data.iloc[0]
            hover_text = (
                f"Dataset: {row['dataset']}<br>Kernel: {row['kernel']}<br>"
                f"BEAST threads: {row['beast_threads']}<br>BEAGLE threads: {row['beagle_threads']}"
            )
            fig.add_trace(
                go.Scatter(
                    x=[row['unique_sites_avg']],
                    y=[row['run_time_min']],
                    mode='markers',
                    name=f"{dataset} {beast_threads}B/{beagle_threads}T",
                    marker=dict(
                        size=16,
                        color=color,
                        symbol=symbol,
                        line=dict(width=2, color='black'),
                        opacity=0.8
                    ),
                    text=[hover_text],
                    customdata=[[row['dataset'], row['kernel'], row['speedup'], row['cost_cpu_min']]],
                    hovertemplate='%{text}<br>' +
                                  'Avg unique sites/partition: %{x:.0f}<br>' +
                                  'Run time: %{y:.2f} min<br>' +
                                  'Speedup: %{customdata[2]:.2f}x<br>' +
                                  'Cost: %{customdata[3]:.1f} cpu-min<extra></extra>',
                )
            )
    else:
        # Each trace is a (beast_threads, beagle_threads) combo (i.e., a marker shape)
        for combo, symbol in combo_to_symbol.items():
            combo_data = partition_data[
                (partition_data['beast_threads'] == combo[0]) &
                (partition_data['beagle_threads'] == combo[1])
            ]
            if combo_data.empty:
                continue

            marker_colors = combo_data['dataset'].map(colors).fillna('gray')
            hover_text = [
                f"Dataset: {row['dataset']}<br>Kernel: {row['kernel']}<br>BEAST threads: {row['beast_threads']}<br>BEAGLE threads: {row['beagle_threads']}"
                for _, row in combo_data.iterrows()
            ]

            fig.add_trace(
                go.Scatter(
                    x=combo_data['unique_sites_avg'],
                    y=combo_data['run_time_min'],
                    mode='markers',
                    name=f"{combo[0]}B/{combo[1]}T",
                    marker=dict(
                        size=16,
                        color=marker_colors,
                        symbol=symbol,
                        line=dict(width=2, color='black'),
                        opacity=0.8
                    ),
                    text=hover_text,
                    customdata=combo_data[['dataset', 'kernel', 'speedup', 'cost_cpu_min']].values,
                    hovertemplate='%{text}<br>' +
                                  'Avg unique sites/partition: %{x:.0f}<br>' +
                                  'Run time: %{y:.2f} min<br>' +
                                  'Speedup: %{customdata[2]:.2f}x<br>' +
                                  'Cost: %{customdata[3]:.1f} cpu-min<extra></extra>',
                )
            )

    # Remove the right-hand annotation legend for marker shapes (legend_html and fig.add_annotation)

    fig.update_layout(
        title={
            'text': f'BEAST Performance: {partition_count} Partition{"s" if partition_count > 1 else ""}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis=dict(
            title='Average Unique Sites per Partition',
            type='log',
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            title='Run Time (minutes)',
            type='log',
            gridcolor='lightgray',
            showgrid=True
        ),
        width=1000,
        height=700,
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            x=1.01,
            y=0.5,
            xanchor='left',
            yanchor='middle',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=12)
        )
    )

    # Save plot
    filename = f'{partition_count}_partition{"s" if partition_count > 1 else ""}_comparison'
    fig.write_html(f'docs/{filename}.html')
    print(f"Created: docs/{filename}.html")

# Create comparison summary
summary_stats = []
for partition_count in partition_counts:
    partition_data = df[df['partitions'] == partition_count]
    for dataset in partition_data['dataset'].unique():
        native_data = partition_data[(partition_data['dataset'] == dataset) & 
                                   (partition_data['kernel'] == 'native')]
        beagle_data = partition_data[(partition_data['dataset'] == dataset) & 
                                   (partition_data['kernel'] == 'beagle_SSE')]
        if not native_data.empty and not beagle_data.empty:
            native_best = native_data['run_time_min'].min()
            beagle_best = beagle_data['run_time_min'].min()
            improvement = (native_best - beagle_best) / native_best * 100
            summary_stats.append({
                'dataset': dataset,
                'partitions': partition_count,
                'native_best_time': native_best,
                'beagle_best_time': beagle_best,
                'improvement_percent': improvement
            })

summary_df = pd.DataFrame(summary_stats)
summary_df.to_csv('docs/kernel_comparison_summary.csv', index=False)

# Create enhanced index page
index_html = """<!DOCTYPE html>
<html>
<head>
    <title>BEAST Performance: Native vs BEAGLE</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
        }
        h1 { 
            color: #333; 
            text-align: center;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .comparison-note {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #2196f3;
        }
        .plot-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .plot-card {
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        .plot-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        .plot-card h3 {
            color: #007bff;
            margin-bottom: 15px;
        }
        .plot-link {
            display: inline-block;
            padding: 10px 25px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 15px;
            transition: background-color 0.3s;
        }
        .plot-link:hover {
            background-color: #0056b3;
        }
        .improvement {
            color: #28a745;
            font-weight: bold;
        }
        .legend-box {
            display: inline-block;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BEAST Performance Analysis: Native vs BEAGLE Kernels</h1>
        
        <div class="comparison-note">
            <h3>Kernel Comparison</h3>
            <div class="legend-box">
                <strong>Marker shapes:</strong> shape = BEAST/BEAGLE threads<br>
                <strong>Color:</strong> dataset
            </div>
            <p><strong>Key findings:</strong></p>
            <ul>
                <li>BEAGLE SSE consistently outperforms native kernel, especially with proper thread configuration</li>
                <li>Native kernel can only use BEAST threads (partition-level parallelization)</li>
                <li>BEAGLE SSE can use both BEAST threads AND BEAGLE threads for better performance</li>
            </ul>
        </div>
        
        <div class="plot-grid">
"""

# Add performance improvement stats to cards
for partition_count in partition_counts:
    partition_data = df[df['partitions'] == partition_count]
    datasets = list(partition_data['dataset'].unique())
    partition_improvements = summary_df[summary_df['partitions'] == partition_count]['improvement_percent']
    avg_improvement = partition_improvements.mean() if len(partition_improvements) > 0 else 0
    index_html += f"""
            <div class="plot-card">
                <h3>{partition_count} Partition{"s" if partition_count > 1 else ""}</h3>
                <p>Datasets: {', '.join(datasets)}</p>
                <a href="{partition_count}_partition{'s' if partition_count > 1 else ''}_comparison.html" class="plot-link">View Comparison →</a>
            </div>
"""

index_html += """
        </div>
        
        <div class="comparison-note">
            <h3>📊 Data Downloads</h3>
            <ul>
                <li><a href="kernel_comparison_summary.csv">Kernel comparison summary (CSV)</a></li>
                <li><a href="experiment_summary.csv">All experiments data (CSV)</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

with open('docs/index.html', 'w') as f:
    f.write(index_html)

# Also save complete experiment data
df.to_csv('docs/experiment_summary.csv', index=False)

print("\nCreated comparison plots showing native vs beagle_SSE performance")
print(f"\nSummary of improvements (beagle_SSE vs native):")
if not summary_df.empty:
    print(summary_df[['dataset', 'partitions', 'improvement_percent']].round(1).to_string(index=False))
else:
    print("No comparison data available")

print(f"\nTotal files created: {len(partition_counts) + 3}")

