import sys
import os
import re
import argparse
import statistics
import matplotlib.pyplot as plt

def parse_log_file(filepath):
    """Parses a log file to extract execution times."""
    times = []
    time_pattern = re.compile(r"in\s+([\d\.]+)\s+seconds")

    try:
        with open(filepath, 'r') as f:
            for line in f:
                match = time_pattern.search(line)
                if match and "total" not in line.lower(): 
                    times.append(float(match.group(1)) * 1000) # Convert to ms immediately
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None

    if not times:
        return None

    label = os.path.basename(filepath).replace(".txt", "").replace("_", " ").title()
    return {"label": label, "times": times}

def save_violin_plot(data_list):
    """Graph 1: Distribution Density (Violin Plot) - Best for outliers."""
    plt.figure(figsize=(10, 6))
    labels = [d['label'] for d in data_list]
    times = [d['times'] for d in data_list]
    
    parts = plt.violinplot(times, showmeans=True, showmedians=True)
    
    # Customizing colors
    for pc in parts['bodies']:
        pc.set_facecolor('#D43F33')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
        
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.title('Performance Density & Distribution (Violin Plot)')
    plt.ylabel('Time (milliseconds)')
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    
    plt.savefig("graph_distribution.png")
    plt.close()
    print("Saved: graph_distribution.png")

def save_comparison_bar(data_list):
    """Graph 2: Simple Average Comparison (Bar Chart)."""
    plt.figure(figsize=(10, 6))
    labels = [d['label'] for d in data_list]
    means = [statistics.mean(d['times']) for d in data_list]
    
    bars = plt.bar(labels, means, color=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'])
    
    plt.title('Average Execution Time (Mean)')
    plt.ylabel('Time (milliseconds)')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                 f'{bar.get_height():.4f} ms', ha='center', va='bottom', fontweight='bold')

    plt.savefig("graph_averages.png")
    plt.close()
    print("Saved: graph_averages.png")

def save_time_series(data_list):
    """Graph 3: Execution Timeline (Line Chart) - To see performance over time."""
    plt.figure(figsize=(12, 6))
    
    for d in data_list:
        plt.plot(d['times'], label=d['label'], alpha=0.8, linewidth=1.5)
        
    plt.title('Execution Time Across Iterations')
    plt.xlabel('Iteration Number')
    plt.ylabel('Time (milliseconds)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig("graph_timeline.png")
    plt.close()
    print("Saved: graph_timeline.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    all_data = []
    for f in args.files:
        data = parse_log_file(f)
        if data:
            all_data.append(data)

    if not all_data:
        print("No data found.")
        sys.exit(1)

    # Generate the 3 separate files
    save_violin_plot(all_data)
    save_comparison_bar(all_data)
    save_time_series(all_data)
