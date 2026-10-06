import plotly.express as px
import plotly.graph_objects as go

def plot_realtime_cpu_memory(history_df):
    if history_df is None or history_df.empty:
        return go.Figure()
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history_df['timestamp'], y=history_df['cpu_usage_percent'],
                             mode='lines', name='System CPU %', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=history_df['timestamp'], y=history_df['memory_usage_percent'],
                             mode='lines', name='System Memory %', line=dict(color='magenta')))
                             
    fig.update_layout(title='Real-time System Resource Usage',
                      xaxis_title='Time', yaxis_title='Percentage',
                      template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0))
    return fig

def plot_risk_distribution(df):
    if df is None or df.empty:
        return go.Figure()
        
    fig = px.histogram(df, x='risk_score', nbins=20, 
                       title='Risk Score Distribution',
                       color_discrete_sequence=['orange'],
                       template='plotly_dark')
    fig.update_layout(xaxis_title='Risk Score', yaxis_title='Count', margin=dict(l=0, r=0, t=30, b=0))
    return fig

def plot_process_history(process_history_df, pid):
    if process_history_df is None or process_history_df.empty:
        return go.Figure()
        
    df = process_history_df[process_history_df['pid'] == pid]
    if df.empty:
        return go.Figure()
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cpu_percent'],
                             mode='lines+markers', name='CPU %', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['memory_percent'],
                             mode='lines+markers', name='Memory %', line=dict(color='magenta')))
                             
    fig.update_layout(title=f'Resource History for PID {pid}',
                      xaxis_title='Time', yaxis_title='Percentage',
                      template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0))
    return fig
