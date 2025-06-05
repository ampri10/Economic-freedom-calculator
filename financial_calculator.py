import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy_financial as npf

def calculate_pension_goal(monthly_exp, current_age, safe_rate=0.04):
    """Calculate the goal amount needed to sustain monthly expenses until age 67"""
    years_until_67 = max(0, 67 - current_age)
    if years_until_67 <= 0:
        return 0
    
    # Calculate present value of annuity (monthly expenses until age 67)
    annual_expenses = monthly_exp * 12
    
    # Using present value of annuity formula: PV = PMT * [(1 - (1+r)^-n) / r]
    if safe_rate > 0:
        #pv_factor = (1 - (1 + safe_rate) ** -years_until_67) / safe_rate
        #goal = annual_expenses * pv_factor
        goal = npf.pv(rate=safe_rate, nper=years_until_67, pmt=-annual_expenses, fv=0)
    else:
        goal = annual_expenses * years_until_67
    
    return goal

def calculate_future_value(initial_value, yearly_payment, rate, years, monthly_exp=None, safe_rate=0.04, mode="freedom", current_age=30):
    """Calculate future values year by year with different modes"""
    values = [initial_value]
    goal_reached_year = None
    goal = None
    goal_reached = 0
    
    if monthly_exp is not None:
        if mode == "freedom":
            goal = (monthly_exp * 12) / safe_rate
        elif mode == "pension":
            goal = calculate_pension_goal(monthly_exp, current_age, safe_rate)
    
    for year in range(1, years + 1):
        if (goal is None or values[-1] < goal) and goal_reached == 0:
            # Still accumulating - add yearly payment and growth
            new_value = values[-1] * (1 + rate) + yearly_payment
        else:
            # Goal reached - different behavior based on mode
            goal_reached = 1
            if goal_reached_year is None:
                goal_reached_year = year
            
            annual_expenses = monthly_exp * 12
            
            if mode == "freedom":
                # Financial freedom: portfolio grows at safe rate minus expenses
                new_value = values[-1] * (1 + safe_rate) - annual_expenses
            elif mode == "pension":
                # Pension mode: portfolio grows at safe rate minus expenses (running down to zero)
                new_value = values[-1] * (1 + safe_rate) - annual_expenses
        
        values.append(new_value)
    
    return values, goal_reached_year, goal

def plot_future_value(initial_value, yearly_payment, rate=0, years=10, monthly_exp=None, safe_rate=0.04, mode="freedom", current_age=30):
    """Create an interactive plotly chart for financial projections"""
    values, goal_reached_year, goal = calculate_future_value(initial_value, yearly_payment, rate, years, monthly_exp, safe_rate, mode, current_age)
    
    # Create year labels starting from 2025
    x = list(range(2025, years + 2026))
    
    fig = go.Figure()
    
    if goal is not None and goal_reached_year is not None:
        # Split data into accumulation and withdrawal phases
        accumulation_years = x[:goal_reached_year]
        accumulation_values = values[:goal_reached_year]
        if goal_reached_year is not None and goal_reached_year > 0:
            withdrawal_years = x[goal_reached_year - 1:]
            withdrawal_values = values[goal_reached_year - 1:]
        else:
            withdrawal_years = []
            withdrawal_values = []
        
        # Accumulation phase
        fig.add_trace(go.Scatter(
            x=accumulation_years,
            y=accumulation_values,
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=6),
            name="Accumulation Phase",
            hovertemplate='<b>Year %{x}</b><br>Value: $%{y:,.0f}<br>Phase: Accumulation<extra></extra>'
        ))
        
        # Withdrawal phase
        phase_name = "Financial Freedom" if mode == "freedom" else "Pension Drawdown"
        phase_color = "orange" if mode == "freedom" else "purple"
        
        fig.add_trace(go.Scatter(
            x=withdrawal_years,
            y=withdrawal_values,
            mode='lines+markers',
            line=dict(color=phase_color, width=3),
            marker=dict(size=6),
            name=phase_name,
            hovertemplate=f'<b>Year %{{x}}</b><br>Value: $%{{y:,.0f}}<br>Phase: {phase_name}<extra></extra>'
        ))
        
        # Add goal line
        fig.add_hline(y=goal, line_dash="dash", line_color="red", 
                     annotation_text=f"Goal: ${goal:,.0f}")
        
        # Add retirement age line for pension mode
        if mode == "pension":
            retirement_year = 2025 + (67 - current_age)
            if retirement_year <= max(x):
                fig.add_vline(x=retirement_year, line_dash="dot", line_color="blue",
                             annotation_text=f"Age 67 ({retirement_year})")
        
    else:
        # Original single phase plot
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
            text= f"${value/1000000:,.2f}m" if value >1000000 else f"${value/1000:,.0f}k",
            showarrow=False,
            yshift=20,
            font=dict(size=10, color="black")
        )
    
    mode_text = "Financial Freedom" if mode == "freedom" else "Pension Planning"
    title = f"{mode_text} - {rate*100:.1f}% Growth Rate"
    if goal is not None:
        title += f" | Goal: ${goal:,.0f} | Safe Rate: {safe_rate*100:.1f}%"
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
        width=1200,
        height=500
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
            value=600000.0,
            step=25000.0,
            help="Starting amount you're investing"
        )
        
        yearly_payment = st.number_input(
            "Annual Contribution ($)",
            min_value=0.0,
            value=60000.0,
            step=5000.0,
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
            value=20,
            help="Number of years to project"
        )
        
        # Financial Planning Mode Selection
        st.subheader("🎯 Planning Mode")
        
        planning_mode = st.radio(
            "Choose your financial planning approach:",
            ["basic", "freedom", "pension"],
            format_func=lambda x: {
                "basic": "📈 Basic Growth (No specific goal)",
                "freedom": "🏖️ Financial Freedom (Sustainable forever)",
                "pension": "🏖️ Pension Planning (Spend down to zero by age 67)"
            }[x],
            help="Select the type of financial planning you want to model"
        )
        
        monthly_exp = None
        safe_rate = 0.04
        current_age = 35
        
        if planning_mode in ["freedom", "pension"]:
            st.subheader("💰 Retirement Parameters")
            
            current_age = st.number_input(
                "Current Age",
                min_value=18,
                max_value=65,
                value=36,
                step=1,
                help="Your current age (used for pension planning)"
            )
            
            monthly_exp = st.number_input(
                "Monthly Living Expenses ($)",
                min_value=0.0,
                value=7500.0,
                step=500.0,
                help="How much you need per month to cover all expenses"
            )
            
            safe_rate = st.slider(
                "Safe Investment Rate (%)",
                min_value=1.0,
                max_value=10.0,
                value=4.0,
                step=0.1,
                help="Conservative growth rate during retirement phase"
            ) / 100
            
            # Show calculated information
            if monthly_exp > 0:
                annual_expenses = monthly_exp * 12
                
                if planning_mode == "freedom":
                    calculated_goal = (monthly_exp * 12) / safe_rate
                    st.info(f"🎯 **Financial Freedom Goal**: ${calculated_goal:,.0f}")
                    st.info(f"💡 **Logic**: Need ${calculated_goal:,.0f} to generate ${annual_expenses:,.0f}/year forever at {safe_rate*100:.1f}% rate")
                
                elif planning_mode == "pension":
                    years_until_67 = max(0, 67 - current_age)
                    calculated_goal = calculate_pension_goal(monthly_exp, current_age, safe_rate)
                    st.info(f"🎯 **Pension Goal**: ${calculated_goal:,.0f}")
                    st.info(f"📅 **Years until 67**: {years_until_67} years")
                    st.info(f"💡 **Logic**: Need ${calculated_goal:,.0f} to spend ${annual_expenses:,.0f}/year until age 67")
                
                st.info(f"💸 **Annual Expenses**: ${annual_expenses:,.0f} (${monthly_exp:,.0f}/month)")
        
        # Calculate button
        calculate = st.button("📈 Calculate & Plot", type="primary")
    
    with col2:
        st.header("📈 Results")
        
        if calculate or st.session_state.get('auto_calculate', False):
            # Calculate values
            values, goal_reached_year, goal = calculate_future_value(initial_value, yearly_payment, rate, years, monthly_exp, safe_rate, planning_mode, current_age)
            final_value = values[-1]
            
            # Calculate contributions based on goal
            if goal is not None and goal_reached_year is not None:
                total_contributions = initial_value + (yearly_payment * (goal_reached_year - 1))
                years_to_goal = goal_reached_year - 1
            else:
                total_contributions = initial_value + (yearly_payment * years)
                years_to_goal = None
            
            total_growth = max(0, final_value - total_contributions) if goal_reached_year is None else max(0, goal - total_contributions)
            
            # Display key metrics based on mode
            if planning_mode == "basic":
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
            
            elif planning_mode in ["freedom", "pension"] and goal is not None and goal_reached_year is not None:
                col2a, col2b, col2c, col2d = st.columns(4)
                
                with col2a:
                    st.metric(
                        "Years to Goal", 
                        f"{years_to_goal}",
                        help="Years needed to reach your target"
                    )
                
                with col2b:
                    goal_label = "Freedom Goal" if planning_mode == "freedom" else "Pension Goal"
                    st.metric(
                        goal_label, 
                        f"${goal:,.0f}",
                        help="Your calculated target amount"
                    )
                
                with col2c:
                    st.metric(
                        "Final Value", 
                        f"${final_value:,.0f}",
                        help="Portfolio value at the end of projection"
                    )
                
                with col2d:
                    if planning_mode == "pension":
                        age_at_end = current_age + years
                        st.metric(
                            "Age at End", 
                            f"{age_at_end}",
                            help="Your age at the end of the projection"
                        )
                    else:
                        st.metric(
                            "Monthly Expenses", 
                            f"${monthly_exp:,.0f}",
                            help="Monthly living expenses covered"
                        )
            
            # Create and display the plot
            fig = plot_future_value(initial_value, yearly_payment, rate, years, monthly_exp, safe_rate, planning_mode, current_age)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed breakdown table
            st.subheader("📋 Year-by-Year Breakdown")
            
            # Create DataFrame for the table
            years_list = list(range(2025, years + 2026))
            phase_list = []
            
            for i, year in enumerate(years_list):
                if planning_mode == "basic":
                    phase_list.append("📈 Growth")
                elif goal is not None and goal_reached_year is not None:
                    if goal_reached_year is not None and i < goal_reached_year:
                        phase_list.append("🟢 Accumulation")
                    else:
                        if planning_mode == "freedom":
                            phase_list.append("🟠 Financial Freedom")
                        else:  # pension mode
                            age_at_year = current_age + i
                            if age_at_year < 67:
                                phase_list.append("🟣 Pension Drawdown")
                            else:
                                phase_list.append("🏖️ Retirement")
                else:
                    phase_list.append("📈 Growth")
            
            df_data = {
                'Year': years_list,
                'Portfolio Value': [f"${val:,.0f}" for val in values],
                'Phase': phase_list
            }
            
            # Add age column for pension mode
            if planning_mode == "pension":
                ages = [current_age + i for i in range(len(years_list))]
                df_data['Age'] = ages
            
            # Add annual change column
            annual_changes = []
            for i, val in enumerate(values):
                if i == 0:
                    annual_changes.append("${0:,.0f}")
                else:
                    change = val - values[i-1]
                    annual_changes.append(f"${change:,.0f}")
            
            df_data['Annual Change'] = annual_changes
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Add some helpful information
    st.markdown("---")
    st.markdown("""
    ### 💡 How to Use This Calculator
    
    **📈 Basic Mode:**
    - Simple portfolio growth projection
    - Shows how your investments grow over time with regular contributions
    
    **🏖️ Financial Freedom Mode:**
    - Input your monthly living expenses
    - Goal = (Monthly Expenses × 12) ÷ Safe Rate
    - Portfolio sustains your lifestyle forever
    - Example: $3,333/month at 4% = $1,000,000 goal
    
    **🏖️ Pension Planning Mode:**
    - Input your current age and monthly expenses  
    - Calculates the exact amount needed to support you until age 67
    - Portfolio runs down to zero by retirement age
    - Uses present value calculations for precise targeting
    
    **Note**: This calculator assumes compound growth and doesn't account for inflation, taxes, or market volatility.
    Safe rates are conservative growth estimates during retirement phases.
    """)
    
    # Auto-calculate checkbox
    st.checkbox(
        "Auto-calculate on parameter change", 
        key='auto_calculate',
        help="Automatically update results when you change parameters"
    )

if __name__ == "__main__":
    main()
