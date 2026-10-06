import matplotlib.pyplot as plt
import numpy as np

def plot_anomaly_distribution(df):
    if df is None or df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center')
        fig.patch.set_facecolor('#0e1117')
        ax.set_facecolor('#0e1117')
        return fig
        
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    categories = ['NORMAL', 'SUSPICIOUS', 'ABNORMAL']
    counts = [len(df[df['classification'] == cat]) for cat in categories]
    colors = ['green', 'orange', 'red']
    
    ax.bar(categories, counts, color=colors)
                  
    ax.set_title('Process Classification Distribution', color='white')
    ax.set_xlabel('Classification', color='white')
    ax.set_ylabel('Count', color='white')
    ax.tick_params(colors='white')
    
    for spine in ax.spines.values():
        spine.set_color('gray')
        
    plt.tight_layout()
    return fig

def plot_feature_correlation(df):
    if df is None or df.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center')
        fig.patch.set_facecolor('#0e1117')
        return fig
        
    features = ['cpu_percent', 'memory_percent', 'num_threads', 'io_read_rate', 'io_write_rate', 'risk_score']
    available_features = [f for f in features if f in df.columns]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#0e1117')
    
    if len(available_features) > 1:
        corr = df[available_features].corr().values
        
        cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
        
        ax.set_xticks(np.arange(len(available_features)))
        ax.set_yticks(np.arange(len(available_features)))
        ax.set_xticklabels(available_features, rotation=45, ha='left', color='white')
        ax.set_yticklabels(available_features, color='white')
        
        for i in range(len(available_features)):
            for j in range(len(available_features)):
                ax.text(j, i, f"{corr[i, j]:.2f}", ha='center', va='center', 
                        color='white' if abs(corr[i, j]) > 0.5 else 'black')
        
        ax.set_title('Feature Correlation Matrix', color='white', pad=20)
        
        # Colorbar
        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label('Correlation', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        cbar.outline.set_edgecolor('gray')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    else:
        ax.text(0.5, 0.5, 'Not enough features', ha='center', va='center', color='white')
        ax.set_facecolor('#0e1117')
        
    plt.tight_layout()
    return fig
