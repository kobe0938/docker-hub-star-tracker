#!/usr/bin/env python3
"""
Docker Hub Pull Count Visualization Script
Generates graphs showing pull count trends over time for tracked repositories.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pytz
import seaborn as sns

def load_and_process_data(csv_file='pull_counts.csv'):
    """Load and process the pull count data."""
    try:
        # Read CSV data
        df = pd.read_csv(csv_file)
        
        # Convert timestamp to datetime, handling both UTC and PST formats
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Handle timezone-aware and timezone-naive timestamps
        pst = pytz.timezone('America/Los_Angeles')
        
        def convert_to_pst(timestamp):
            if pd.isna(timestamp):
                return timestamp
            if timestamp.tzinfo is not None:
                return timestamp.tz_convert(pst)
            else:
                # Assume UTC for timezone-naive timestamps
                return pytz.utc.localize(timestamp).astimezone(pst)
        
        # For timezone-naive timestamps, assume UTC and convert to PST
        df['timestamp_pst'] = df['timestamp'].apply(convert_to_pst)
        
        # Use the PST timestamp as the main timestamp
        df['timestamp'] = df['timestamp_pst']
        
        # Remove any rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_individual_repo_graphs(df):
    """Create separate graphs for each repository with annotated values."""
    repositories = df['repository'].unique()
    figures = []
    
    for repo in repositories:
        repo_data = df[df['repository'] == repo].copy()
        namespace = repo_data['namespace'].iloc[0]
        
        # Set up the plot style
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot the line with markers
        line = ax.plot(repo_data['timestamp'], repo_data['pull_count'], 
                      marker='o', linewidth=3, markersize=8,
                      color='#1f77b4', markerfacecolor='white', 
                      markeredgewidth=2, markeredgecolor='#1f77b4')
        
        # Annotate each point with the pull count value
        for i, (timestamp, count) in enumerate(zip(repo_data['timestamp'], repo_data['pull_count'])):
            ax.annotate(f'{count:,}', 
                       (timestamp, count),
                       textcoords="offset points", 
                       xytext=(0,15), 
                       ha='center',
                       fontsize=10,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Customize the plot
        ax.set_title(f'{namespace}/{repo} - Docker Hub Pull Count Trends', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Time (PST)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Pull Count', fontsize=12, fontweight='bold')
        
        # Format x-axis to show dates nicely
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
        if len(repo_data) > 6:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=0)
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Format y-axis with commas
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        # Add some padding to y-axis to accommodate annotations
        y_min, y_max = ax.get_ylim()
        y_padding = (y_max - y_min) * 0.1
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        figures.append((fig, f'{namespace}_{repo}'))
    
    return figures

def create_summary_stats(df):
    """Create a summary statistics table."""
    print("\n" + "="*60)
    print("DOCKER HUB PULL COUNT SUMMARY STATISTICS")
    print("="*60)
    
    for repo in df['repository'].unique():
        repo_data = df[df['repository'] == repo]
        namespace = repo_data['namespace'].iloc[0]
        
        print(f"\n📦 {namespace}/{repo}")
        print("-" * 40)
        
        current_pulls = repo_data['pull_count'].iloc[-1]
        initial_pulls = repo_data['pull_count'].iloc[0]
        total_growth = current_pulls - initial_pulls
        
        # Calculate time range
        start_time = repo_data['timestamp'].iloc[0]
        end_time = repo_data['timestamp'].iloc[-1]
        time_range = end_time - start_time
        hours = time_range.total_seconds() / 3600
        
        avg_growth_rate = total_growth / hours if hours > 0 else 0
        
        print(f"Current Pull Count: {current_pulls:,}")
        print(f"Total Growth: +{total_growth:,} pulls")
        print(f"Time Period: {hours:.1f} hours")
        print(f"Average Growth Rate: {avg_growth_rate:.1f} pulls/hour")
        print(f"Latest Update: {end_time.strftime('%Y-%m-%d %H:%M:%S PST')}")

def main():
    """Main function to generate all visualizations."""
    print("🚀 Generating Docker Hub Pull Count Visualizations...")
    
    # Load data
    df = load_and_process_data()
    if df is None:
        print("❌ Failed to load data. Please check if pull_counts.csv exists.")
        return
    
    print(f"📊 Loaded {len(df)} data points for {df['repository'].nunique()} repositories")
    
    # Create individual repository graphs
    print("📈 Creating individual repository trend graphs...")
    repo_figures = create_individual_repo_graphs(df)
    
    for fig, repo_name in repo_figures:
        filename = f'docker_hub_trends_{repo_name}.png'
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {filename}")
    
    # Show summary statistics
    create_summary_stats(df)
    
    # Display plots
    plt.show()
    
    print("\n🎉 Visualization complete! Check the generated PNG files.")

if __name__ == "__main__":
    main()
