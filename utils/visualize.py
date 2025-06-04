# utils/visualize.py
import streamlit as st
import pandas as pd
import plotly.express as px

def display_compliance_summary(analysis_results, regulations):
    # Calculate compliance scores
    compliance_data = []
    for result in analysis_results:
        for match in result['matches']:
            compliance_data.append({
                "regulation": match['regulation'],
                "score": match['similarity_score'],
                "clause": match['clause_id']
            })
    
    df = pd.DataFrame(compliance_data)
    
    if not df.empty:
        # Average compliance by regulation
        avg_scores = df.groupby('regulation')['score'].mean().reset_index()
        
        st.subheader("Average Compliance by Regulation")
        fig = px.bar(avg_scores, x='regulation', y='score', 
                     title="Compliance Scores by Regulatory Framework")
        st.plotly_chart(fig)
        
        # Detailed matches
        st.subheader("Top Matches for Each Control")
        for i, result in enumerate(analysis_results, 1):
            st.markdown(f"**Control {i}:** {result['control_text'][:100]}...")
            matches_df = pd.DataFrame(result['matches'])
            st.dataframe(matches_df)

def display_gap_analysis(analysis_results, regulations):
    # Identify gaps (low similarity scores)
    gap_data = []
    threshold = 0.5  # Consider scores below this as gaps
    
    for result in analysis_results:
        for match in result['matches']:
            if match['similarity_score'] < threshold:
                gap_data.append({
                    "regulation": match['regulation'],
                    "clause": match['clause_id'],
                    "score": match['similarity_score']
                })
    
    if gap_data:
        gap_df = pd.DataFrame(gap_data)
        st.subheader("Potential Compliance Gaps")
        
        # Group by regulation
        gap_counts = gap_df['regulation'].value_counts().reset_index()
        gap_counts.columns = ['regulation', 'gap_count']
        
        fig = px.pie(gap_counts, names='regulation', values='gap_count',
                     title="Gap Distribution by Regulation")
        st.plotly_chart(fig)
        
        st.dataframe(gap_df)
    else:
        st.success("No significant compliance gaps detected!")