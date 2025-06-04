import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def calculate_future_value(initial_value, yearly_payment, rate, years):
    """Calculate future values year by year"""
    values = [initial_value]
    
    for year in range(1, years + 1):
        new_value = values[-1] * (1 + rate) + yearly_payment
        values.append(new_value)
    
    return values

def plot_future_value(initial_value, yearly_payment, rate=0, years=10):
    """Create an interactive plotly chart for financial projections"""
    values = calculate_future_value(initial_value, yearly_payment, rate, years)
    
    # Create year labels starting from 2025
    x = list(range(2025, years + 2026))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=values,
        mode='lines+markers',
        line=dict(color='royalblue', width=3),
        marker=dict(size=6),
        name="Projected Value",
        hovertemplate='<b>Year %{x}</b><br>Value: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add value annotations
    for year, value in zip(x, values):
        fig.add_annotation(
            x=year,
            y=value,
            text=f"${value:,.0f}",
            showarrow=False,
            yshift=20,
            font=dict(size=10, color="black")
        )
    
    fig.update_layout(
        title=f"Portfolio Projection - Assuming a {rate*100:.1f}% Annual Return",
        xaxis_title="Year",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
        width=800,
        height=500,
        showlegend=False
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="Financial Calculator",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Financial Portfolio Calculator")
    st.markdown("Calculate and visualize your investment portfolio growth over time")
    
    # Create two columns for input and results
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📊 Input Parameters")
        
        # Input fields
        initial_value = st.number_input(
            "Initial Investment ($)",
            min_value=0.0,
            value=10000.0,
            step=1000.0,
            help="Starting amount you're investing"
        )
        
        yearly_payment = st.number_input(
            "Annual Contribution ($)",
            min_value=0.0,
            value=5000.0,
            step=500.0,
            help="Amount you'll add each year"
        )
        
        rate = st.slider(
            "Expected Annual Return (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.1,
            help="Expected annual return rate"
        ) / 100
        
        years = st.slider(
            "Investment Period (Years)",
            min_value=1,
            max_value=50,
            value=10,
            help="Number of years to project"
        )
        
        # Calculate button
        calculate = st.button("📈 Calculate & Plot", type="primary")
    
    with col2:
        st.header("📈 Results")
        
        if calculate or st.session_state.get('auto_calculate', False):
            # Calculate values
            values = calculate_future_value(initial_value, yearly_payment, rate, years)
            final_value = values[-1]
            total_contributions = initial_value + (yearly_payment * years)
            total_growth = final_value - total_contributions
            
            # Display key metrics
            col2a, col2b, col2c = st.columns(3)
            
            with col2a:
                st.metric(
                    "Final Value", 
                    f"${final_value:,.0f}",
                    delta=f"${total_growth:,.0f}"
                )
            
            with col2b:
                st.metric(
                    "Total Contributions", 
                    f"${total_contributions:,.0f}"
                )
            
            with col2c:
                roi_percentage = (total_growth / total_contributions) * 100 if total_contributions > 0 else 0
                st.metric(
                    "Total Return", 
                    f"{roi_percentage:.1f}%"
                )
            
            # Create and display the plot
            fig = plot_future_value(initial_value, yearly_payment, rate, years)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed breakdown table
            st.subheader("📋 Year-by-Year Breakdown")
            
            # Create DataFrame for the table
            years_list = list(range(2025, years + 2026))
            df = pd.DataFrame({
                'Year': years_list,
                'Portfolio Value': [f"${val:,.0f}" for val in values],
                'Annual Growth': [f"${val - values[i] if i > 0 else 0:,.0f}" for i, val in enumerate(values)]
            })
            
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Add some helpful information
    st.markdown("---")
    st.markdown("""
    ### 💡 How to Use This Calculator
    
    1. **Initial Investment**: Enter your starting investment amount
    2. **Annual Contribution**: Amount you plan to add each year
    3. **Expected Annual Return**: Conservative estimates are typically 6-8% for diversified portfolios
    4. **Investment Period**: How many years you plan to invest
    
    **Note**: This calculator assumes compound growth and doesn't account for inflation, taxes, or market volatility.
    """)
    
    # Auto-calculate checkbox
    st.checkbox(
        "Auto-calculate on parameter change", 
        key='auto_calculate',
        help="Automatically update results when you change parameters"
    )

if __name__ == "__main__":
    main()